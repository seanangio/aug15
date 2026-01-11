"""
Text analysis utilities for processing speeches.

This module provides functions for tokenization, stopword removal, TF-IDF calculation,
and sentiment analysis using NLTK.
"""

import re
from typing import Dict, List

import nltk
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


# Auto-download required NLTK data on first import
def _download_nltk_data():
    """Download required NLTK data if not already present."""
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)

    try:
        nltk.data.find('corpora/opinion_lexicon')
    except LookupError:
        nltk.download('opinion_lexicon', quiet=True)


# Call on module import
_download_nltk_data()


def tokenize_text(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tokenize text column into individual words.

    Converts text to lowercase and splits into words (alphanumeric sequences).
    Each row in the result represents one word token.

    Args:
        df: DataFrame with columns [year, pm, party, text]

    Returns:
        DataFrame with columns [year, pm, party, word] where each row is one word
    """
    # Explode each text into words
    rows = []
    for _, row in df.iterrows():
        # Skip rows with missing text (NaN values)
        if pd.isna(row['text']):
            continue

        # Convert to lowercase and extract words (alphanumeric sequences)
        words = re.findall(r'\b\w+\b', row['text'].lower())
        for word in words:
            rows.append({
                'year': row['year'],
                'pm': row['pm'],
                'party': row['party'],
                'word': word
            })

    return pd.DataFrame(rows)


def remove_stopwords(df_tidy: pd.DataFrame) -> pd.DataFrame:
    """
    Remove English stopwords from tokenized dataframe.

    Args:
        df_tidy: Tokenized DataFrame with 'word' column

    Returns:
        DataFrame with stopwords removed
    """
    from nltk.corpus import stopwords

    stop_words = set(stopwords.words('english'))

    return df_tidy[~df_tidy['word'].isin(stop_words)].copy()


def calculate_tf_idf(df_tidy: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate TF-IDF scores for words by year.

    TF-IDF (Term Frequency-Inverse Document Frequency) measures the importance
    of a word in a document (year) relative to the entire corpus.

    Args:
        df_tidy: Tokenized DataFrame with columns [year, pm, party, word]

    Returns:
        DataFrame with columns [year, pm, party, word, n, tf_idf] sorted by tf_idf descending
    """
    # Count words per year
    word_counts = df_tidy.groupby(['year', 'pm', 'party', 'word']).size().reset_index(name='n')

    # Prepare documents (one per year)
    year_texts = df_tidy.groupby('year')['word'].apply(lambda x: ' '.join(x)).reset_index()
    year_texts.columns = ['year', 'text']

    # Calculate TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(year_texts['text'])
    feature_names = vectorizer.get_feature_names_out()

    # Convert to dataframe
    tfidf_scores = []
    for idx, year in enumerate(year_texts['year']):
        # Get TF-IDF scores for this year
        scores = tfidf_matrix[idx].toarray()[0]
        for word_idx, score in enumerate(scores):
            if score > 0:  # Only include non-zero scores
                tfidf_scores.append({
                    'year': year,
                    'word': feature_names[word_idx],
                    'tf_idf': score
                })

    tfidf_df = pd.DataFrame(tfidf_scores)

    # Merge with word counts to get pm and party information
    result = word_counts.merge(tfidf_df, on=['year', 'word'], how='left')
    result['tf_idf'] = result['tf_idf'].fillna(0)

    return result.sort_values('tf_idf', ascending=False)


def calculate_sentiment_words(df_nonstop: pd.DataFrame) -> pd.DataFrame:
    """
    Label words as positive or negative using NLTK opinion lexicon.

    Args:
        df_nonstop: Tokenized DataFrame without stopwords

    Returns:
        DataFrame with additional 'sentiment' column ('positive' or 'negative')
    """
    from nltk.corpus import opinion_lexicon

    positive_words = set(opinion_lexicon.positive())
    negative_words = set(opinion_lexicon.negative())

    # Add sentiment column
    df = df_nonstop.copy()

    # Filter to only words in opinion lexicon
    df = df[
        df['word'].isin(positive_words) | df['word'].isin(negative_words)
    ].copy()

    # Assign sentiment
    df['sentiment'] = df['word'].apply(
        lambda w: 'positive' if w in positive_words else 'negative'
    )

    return df


def calculate_net_sentiment(df_bing: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate net sentiment (positive - negative word counts) by year.

    Args:
        df_bing: DataFrame with sentiment-labeled words

    Returns:
        DataFrame with columns [year, pm, party, positive, negative, sentiment]
        where sentiment = positive - negative
    """
    # Count positive and negative words per year
    sentiment_counts = df_bing.groupby(
        ['year', 'pm', 'party', 'sentiment']
    ).size().reset_index(name='count')

    # Pivot to get positive and negative as columns
    pivoted = sentiment_counts.pivot_table(
        index=['year', 'pm', 'party'],
        columns='sentiment',
        values='count',
        fill_value=0
    ).reset_index()

    # Calculate net sentiment
    pivoted['sentiment'] = pivoted['positive'] - pivoted['negative']

    return pivoted


def count_specific_word(df_tidy: pd.DataFrame, word: str) -> pd.DataFrame:
    """
    Count occurrences of a specific word across years.

    Args:
        df_tidy: Tokenized DataFrame
        word: Word to count (case-insensitive)

    Returns:
        DataFrame with counts by year, pm, party
    """
    word_lower = word.lower()

    # Filter to the specific word
    word_df = df_tidy[df_tidy['word'] == word_lower].copy()

    # Count by year, pm, party
    counts = word_df.groupby(['year', 'pm', 'party']).size().reset_index(name='n')

    # Add rows for years with 0 counts (except 1962 and 1995)
    all_years = df_tidy[
        (df_tidy['year'] != 1962) & (df_tidy['year'] != 1995)
    ][['year', 'pm', 'party']].drop_duplicates()

    # Merge to include zero counts
    result = all_years.merge(counts, on=['year', 'pm', 'party'], how='left')
    result['n'] = result['n'].fillna(0).astype(int)

    return result.sort_values('year')
