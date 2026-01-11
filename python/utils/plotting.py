"""
Plotting utilities for creating interactive visualizations with Plotly.

This module replicates the plots from the R Shiny app using Plotly.
"""

from typing import Optional, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Color palette (extracted from ggplot2 default colors)
PARTY_COLORS = {
    'BJP': '#F8766D',          # Red-ish
    'INC': '#7CAE00',          # Green
    'Janata Dal': '#00BFC4',   # Cyan
    'Janata Party': '#C77CFF'  # Purple
}

# Base styling to match R Shiny app
PLOT_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
}

# Font and size settings to match Shiny app (base_size = 24)
LAYOUT_CONFIG = {
    'font': {'size': 16, 'family': 'Arial, sans-serif', 'color': 'black'},
    'plot_bgcolor': 'white',
    'paper_bgcolor': 'white',
    'hovermode': 'closest',
    'title': {'font': {'color': 'black', 'size': 18}},
}


def apply_theme(fig: go.Figure) -> go.Figure:
    """
    Apply consistent theming to match the R Shiny app.

    Args:
        fig: Plotly figure object

    Returns:
        Themed figure
    """
    fig.update_layout(
        **LAYOUT_CONFIG,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(color='black')
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            showline=True,
            linecolor='black',
            title_font=dict(color='black'),
            tickfont=dict(color='black')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            showline=True,
            linecolor='black',
            title_font=dict(color='black'),
            tickfont=dict(color='black')
        ),
    )

    # Update all axes (for faceted plots)
    fig.update_xaxes(title_font=dict(color='black'), tickfont=dict(color='black'))
    fig.update_yaxes(title_font=dict(color='black'), tickfont=dict(color='black'))

    return fig


def plot_speech_length(df: pd.DataFrame) -> go.Figure:
    """
    Create scatter plot of speech length (word count) over time.

    Args:
        df: Tokenized DataFrame with columns [year, pm, party, word]

    Returns:
        Plotly figure
    """
    # Count words per speech
    word_counts = df.groupby(['year', 'pm', 'party']).size().reset_index(name='word_count')

    # Create hover text
    word_counts['hover_text'] = word_counts.apply(
        lambda row: f"{row['year']}: {row['word_count']:,}", axis=1
    )

    fig = px.scatter(
        word_counts,
        x='year',
        y=word_counts['word_count'] / 1000,  # Convert to thousands
        color='party',
        hover_data={'hover_text': True, 'year': False, 'word_count': False, 'party': False},
        color_discrete_map=PARTY_COLORS,
        title='Total words per speech'
    )

    fig.update_traces(marker=dict(size=12), hovertemplate='%{customdata[0]}')
    fig.update_xaxes(title_text='')
    fig.update_yaxes(title_text='Words (Thousands)')
    fig.update_layout(legend_title_text='Party')

    return apply_theme(fig)


def plot_freq_words(df: pd.DataFrame, facet_var: str = 'none', max_words: int = 12) -> go.Figure:
    """
    Create horizontal bar chart of most frequent words.

    Args:
        df: Tokenized DataFrame without stopwords
        facet_var: Variable to facet by ('none', 'year', 'pm', 'party')
        max_words: Number of top words to display

    Returns:
        Plotly figure
    """
    if facet_var == 'none':
        # Count words across all data
        word_counts = df['word'].value_counts().head(max_words).reset_index()
        word_counts.columns = ['word', 'n']

        fig = px.bar(
            word_counts.sort_values('n'),
            x='n',
            y='word',
            orientation='h',
            title='Most frequent words among included speeches',
            hover_data={'n': ':,'}
        )
        fig.update_traces(hovertemplate='%{x:,}')
        fig.update_xaxes(title_text='Word count')
        fig.update_yaxes(title_text='')

    else:
        # Count words by facet variable
        word_counts = df.groupby([facet_var, 'word']).size().reset_index(name='n')
        word_counts = word_counts.groupby(facet_var).apply(
            lambda x: x.nlargest(max_words, 'n')
        ).reset_index(drop=True)

        fig = px.bar(
            word_counts,
            x='n',
            y='word',
            color=facet_var,
            facet_col=facet_var,
            facet_col_wrap=3,
            orientation='h',
            title='Most frequent words among included speeches',
            hover_data={'n': ':,'},
            color_discrete_map=PARTY_COLORS if facet_var == 'party' else None
        )

        fig.update_traces(hovertemplate='%{x:,}')
        fig.update_xaxes(title_text='Word count', matches=None)
        fig.update_yaxes(title_text='', matches=None)
        fig.for_each_yaxis(lambda yaxis: yaxis.update(categoryorder='total ascending'))

    return apply_theme(fig)


def plot_tf_idf(df: pd.DataFrame, max_words: int = 12) -> go.Figure:
    """
    Create faceted bar charts of most important words by TF-IDF score.

    Args:
        df: DataFrame with TF-IDF scores
        max_words: Number of top words per year

    Returns:
        Plotly figure
    """
    # Get top words per year
    top_words = df.groupby('year').apply(
        lambda x: x.nlargest(max_words, 'tf_idf')
    ).reset_index(drop=True)

    fig = px.bar(
        top_words,
        x='tf_idf',
        y='word',
        facet_col='year',
        facet_col_wrap=4,
        facet_row_spacing=0.01,  # Add minimal spacing to avoid error
        facet_col_spacing=0.03,
        orientation='h',
        title="Most 'important' words according to TF-IDF",
        hover_data={'tf_idf': ':.4f'},
        height=max(600, len(top_words['year'].unique()) * 80)  # Dynamic height
    )

    fig.update_traces(hovertemplate='%{x:.4f}')
    fig.update_xaxes(title_text='TF-IDF', matches=None)
    fig.update_yaxes(title_text='', matches=None)
    fig.for_each_yaxis(lambda yaxis: yaxis.update(categoryorder='total ascending'))

    return apply_theme(fig)


def plot_sentiment_words(
    df: pd.DataFrame,
    facet_var: str = 'none',
    max_words: int = 12
) -> go.Figure:
    """
    Create bar chart of most frequent positive and negative words.

    Args:
        df: DataFrame with sentiment-labeled words
        facet_var: Variable to facet by ('none', 'year', 'pm', 'party')
        max_words: Number of top words to display

    Returns:
        Plotly figure
    """
    # Sentiment colors matching R Shiny app
    sentiment_colors = {'positive': '#00BFC4', 'negative': '#F8766D'}

    if facet_var == 'none':
        # Count words by sentiment
        word_counts = df.groupby(['word', 'sentiment']).size().reset_index(name='n')
        word_counts = word_counts.nlargest(max_words, 'n')

        fig = px.bar(
            word_counts.sort_values('n'),
            x='n',
            y='word',
            color='sentiment',
            orientation='h',
            title='Most frequent positive and negative words',
            hover_data={'n': True},
            color_discrete_map=sentiment_colors
        )
        fig.update_traces(hovertemplate='%{x}')
        fig.update_xaxes(title_text='Word Count')
        fig.update_yaxes(title_text='')
        fig.update_layout(legend_title_text='Sentiment')

    else:
        # Count words by facet variable and sentiment
        word_counts = df.groupby([facet_var, 'word', 'sentiment']).size().reset_index(name='n')
        word_counts = word_counts.groupby(facet_var).apply(
            lambda x: x.nlargest(max_words, 'n')
        ).reset_index(drop=True)

        fig = px.bar(
            word_counts,
            x='n',
            y='word',
            color='sentiment',
            facet_col=facet_var,
            facet_col_wrap=3,
            orientation='h',
            title='Most frequent positive and negative words',
            hover_data={'n': True},
            color_discrete_map=sentiment_colors
        )

        fig.update_traces(hovertemplate='%{x}')
        fig.update_xaxes(title_text='Word Count', matches=None)
        fig.update_yaxes(title_text='', matches=None)
        fig.for_each_yaxis(lambda yaxis: yaxis.update(categoryorder='total ascending'))
        fig.update_layout(legend_title_text='Sentiment')

    return apply_theme(fig)


def plot_net_sentiment(df: pd.DataFrame) -> go.Figure:
    """
    Create scatter plot of net sentiment over time.

    Args:
        df: DataFrame with net sentiment scores

    Returns:
        Plotly figure
    """
    # Create hover text
    df['hover_text'] = df.apply(
        lambda row: f"{row['year']}: {row['positive']} - {row['negative']} = {row['sentiment']}",
        axis=1
    )

    fig = px.scatter(
        df,
        x='year',
        y='sentiment',
        color='party',
        hover_data={'hover_text': True, 'year': False, 'sentiment': False, 'party': False},
        color_discrete_map=PARTY_COLORS,
        title='Difference in Counts of Positive and Negative Words'
    )

    # Add horizontal line at y=0
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=2)

    fig.update_traces(marker=dict(size=12), hovertemplate='%{customdata[0]}')
    fig.update_xaxes(title_text='')
    fig.update_yaxes(title_text='Net Sentiment')
    fig.update_layout(legend_title_text='Party')

    return apply_theme(fig)


def plot_specific_word_trend(df: pd.DataFrame, word: str) -> go.Figure:
    """
    Create line and scatter plot showing frequency of a specific word over time.

    Args:
        df: DataFrame with word counts by year
        word: The word being tracked

    Returns:
        Plotly figure
    """
    # Create hover text
    df['hover_text'] = df.apply(
        lambda row: f"{row['year']}: {row['n']}", axis=1
    )

    fig = px.scatter(
        df,
        x='year',
        y='n',
        color='party',
        hover_data={'hover_text': True, 'year': False, 'n': False, 'party': False},
        color_discrete_map=PARTY_COLORS,
        title=f"Frequency of the term '{word}' among speeches"
    )

    # Add line connecting points
    fig.add_trace(
        go.Scatter(
            x=df['year'],
            y=df['n'],
            mode='lines',
            line=dict(color='black', width=1),
            showlegend=False,
            hoverinfo='skip'
        )
    )

    fig.update_traces(marker=dict(size=12), selector=dict(mode='markers'))
    fig.update_traces(hovertemplate='%{customdata[0]}', selector=dict(mode='markers'))
    fig.update_xaxes(title_text='')
    fig.update_yaxes(title_text='Term Count')
    fig.update_layout(legend_title_text='Party')

    return apply_theme(fig)


# Plot type explanations (matching R tribble)
PLOT_EXPLANATIONS = {
    'Speech Length': "'Speech Length' is a simple count of all words in a speech over time.",
    'Most Frequent Words': "'Most Frequent Words' plots the most frequent words among included speeches, after excluding a generic list of stopwords (a, the, etc). It can be faceted by variables like year, party, or prime minister.",
    'Most Important Words': "'Most Important Words' sorts words according to TF-IDF, which is a statistic that attempts to measure the 'importance' of a word in a speech by adjusting the frequency of a word by how rarely it is otherwise used.",
    '+/- Sentiment Words': "'+/- Sentiment Words' uses the NLTK opinion lexicon to label words among included speeches as either positive or negative. It then plots the most frequent positive and/or negative words.",
    'Net Sentiment': "'Net Sentiment' plots the difference between the number of positive and negative words as determined by the NLTK opinion lexicon.",
    'Specific Word Trend': "'Specific Word Trend' plots the counts of any user-given word. 'freedom' is provided as an example."
}


def get_plot_explanation(plot_type: str) -> str:
    """
    Get explanation text for a given plot type.

    Args:
        plot_type: Name of the plot type

    Returns:
        Explanation string
    """
    return PLOT_EXPLANATIONS.get(plot_type, "")
