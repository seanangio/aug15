"""
Unit tests for data_prep module.
"""

import pandas as pd
import pytest
from utils.data_prep import filter_corpus, get_current_n


def test_filter_corpus():
    """Test corpus filtering functionality."""
    # Create sample data
    df = pd.DataFrame({
        'year': [1947, 1948, 1949, 1950],
        'pm': ['Nehru', 'Nehru', 'Nehru', 'Nehru'],
        'party': ['INC', 'INC', 'INC', 'INC'],
        'text': ['Speech 1', 'Speech 2', 'Speech 3', 'Speech 4']
    })

    # Test year range filtering
    filtered = filter_corpus(df, (1948, 1949), ['Nehru'], ['INC'])
    assert len(filtered) == 2
    assert filtered['year'].min() == 1948
    assert filtered['year'].max() == 1949

    # Test PM filtering
    df_multi = df.copy()
    df_multi.loc[2:3, 'pm'] = 'Modi'
    filtered = filter_corpus(df_multi, (1947, 1950), ['Nehru'], ['INC'])
    assert len(filtered) == 2
    assert all(filtered['pm'] == 'Nehru')

    # Test party filtering
    df_multi['party'] = ['INC', 'INC', 'BJP', 'BJP']
    filtered = filter_corpus(df_multi, (1947, 1950), ['Nehru', 'Modi'], ['BJP'])
    assert len(filtered) == 2
    assert all(filtered['party'] == 'BJP')

    # Test column selection
    filtered = filter_corpus(df, (1947, 1950), ['Nehru'], ['INC'])
    assert list(filtered.columns) == ['year', 'pm', 'party', 'text']


def test_get_current_n():
    """Test speech count message generation."""
    # Create sample dataframes
    df_full = pd.DataFrame({'year': range(1947, 2024)})  # 77 speeches
    df_partial = pd.DataFrame({'year': range(1947, 2000)})  # 53 speeches

    # Test full dataset
    assert get_current_n(df_full, 77) == "77 speeches included."

    # Test partial dataset
    assert get_current_n(df_partial, 77) == "53 of 77 speeches included."

    # Test edge case - empty dataset
    df_empty = pd.DataFrame({'year': []})
    assert get_current_n(df_empty, 77) == "0 of 77 speeches included."


def test_filter_corpus_empty_result():
    """Test that filtering returns empty dataframe when no matches."""
    df = pd.DataFrame({
        'year': [1947, 1948],
        'pm': ['Nehru', 'Nehru'],
        'party': ['INC', 'INC'],
        'text': ['Speech 1', 'Speech 2']
    })

    # Filter with non-existent party
    filtered = filter_corpus(df, (1947, 1948), ['Nehru'], ['BJP'])
    assert len(filtered) == 0
    assert list(filtered.columns) == ['year', 'pm', 'party', 'text']
