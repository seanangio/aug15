"""
Unit tests for text_analysis module.
"""

import pandas as pd
import pytest
from utils.text_analysis import (
    tokenize_text,
    remove_stopwords,
    count_specific_word
)


def test_tokenize_text():
    """Test text tokenization."""
    df = pd.DataFrame({
        'year': [1947, 1948],
        'pm': ['Nehru', 'Nehru'],
        'party': ['INC', 'INC'],
        'text': ['Hello world', 'Testing tokenization']
    })

    result = tokenize_text(df)

    # Check structure
    assert list(result.columns) == ['year', 'pm', 'party', 'word']

    # Check word count
    assert len(result) == 4  # 2 words + 2 words

    # Check lowercasing
    assert 'hello' in result['word'].values
    assert 'Hello' not in result['word'].values

    # Check metadata preserved
    assert all(result['pm'] == 'Nehru')


def test_tokenize_text_punctuation():
    """Test that tokenization handles punctuation correctly."""
    df = pd.DataFrame({
        'year': [1947],
        'pm': ['Nehru'],
        'party': ['INC'],
        'text': ["Hello, world! This is a test."]
    })

    result = tokenize_text(df)

    # Check that words are extracted without punctuation
    assert 'hello' in result['word'].values
    assert 'world' in result['word'].values
    assert 'Hello,' not in result['word'].values


def test_remove_stopwords():
    """Test stopword removal."""
    df = pd.DataFrame({
        'year': [1947] * 6,
        'pm': ['Nehru'] * 6,
        'party': ['INC'] * 6,
        'word': ['the', 'freedom', 'is', 'important', 'and', 'necessary']
    })

    result = remove_stopwords(df)

    # Check that common stopwords are removed
    assert 'the' not in result['word'].values
    assert 'is' not in result['word'].values
    assert 'and' not in result['word'].values

    # Check that content words remain
    assert 'freedom' in result['word'].values
    assert 'important' in result['word'].values
    assert 'necessary' in result['word'].values


def test_count_specific_word():
    """Test specific word counting."""
    df = pd.DataFrame({
        'year': [1947, 1947, 1948, 1948, 1948],
        'pm': ['Nehru', 'Nehru', 'Nehru', 'Nehru', 'Nehru'],
        'party': ['INC', 'INC', 'INC', 'INC', 'INC'],
        'word': ['freedom', 'democracy', 'freedom', 'freedom', 'india']
    })

    result = count_specific_word(df, 'freedom')

    # Check that we get counts by year
    assert len(result) >= 2  # At least 2 years

    # Check counts
    year_1947 = result[result['year'] == 1947]
    year_1948 = result[result['year'] == 1948]

    assert year_1947['n'].values[0] == 1
    assert year_1948['n'].values[0] == 2


def test_count_specific_word_case_insensitive():
    """Test that word counting is case-insensitive."""
    df = pd.DataFrame({
        'year': [1947, 1947],
        'pm': ['Nehru', 'Nehru'],
        'party': ['INC', 'INC'],
        'word': ['freedom', 'freedom']  # Words should already be lowercase from tokenization
    })

    result = count_specific_word(df, 'FREEDOM')  # Search in uppercase

    # Should find both instances (search term gets lowercased)
    assert result[result['year'] == 1947]['n'].values[0] == 2


def test_tokenize_text_empty():
    """Test tokenization with empty text."""
    df = pd.DataFrame({
        'year': [1947],
        'pm': ['Nehru'],
        'party': ['INC'],
        'text': ['']
    })

    result = tokenize_text(df)

    # Should return empty dataframe
    assert len(result) == 0
    # When empty, pandas might not preserve columns, so just check length
