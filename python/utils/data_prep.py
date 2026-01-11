"""
Data preparation utilities for Indian Independence Day speeches corpus.

This module provides functions for loading and filtering the corpus data.
"""

from pathlib import Path
from typing import List, Tuple

import pandas as pd
import streamlit as st


@st.cache_data
def load_corpus() -> pd.DataFrame:
    """
    Load the corpus CSV file with caching.

    Returns:
        DataFrame with columns: year, pm, party, title, footnote, source, url, text
    """
    data_path = Path(__file__).parent.parent / "data" / "corpus.csv"
    df = pd.read_csv(data_path)

    # Ensure year is integer type
    df['year'] = df['year'].astype(int)

    return df


def filter_corpus(
    df: pd.DataFrame,
    year_range: Tuple[int, int],
    pms: List[str],
    parties: List[str]
) -> pd.DataFrame:
    """
    Filter corpus DataFrame based on year range, prime ministers, and parties.

    Args:
        df: Input corpus DataFrame
        year_range: Tuple of (min_year, max_year) inclusive
        pms: List of prime minister names to include
        parties: List of political parties to include

    Returns:
        Filtered DataFrame containing only selected columns and rows
    """
    filtered = df[
        (df['year'] >= year_range[0]) &
        (df['year'] <= year_range[1]) &
        (df['pm'].isin(pms)) &
        (df['party'].isin(parties))
    ].copy()

    # Select only necessary columns (matching R version)
    return filtered[['year', 'pm', 'party', 'text']]


def get_current_n(df: pd.DataFrame, total_speeches: int = 77) -> str:
    """
    Get a string describing how many speeches are currently included.

    Note: Total is 77 because 2 speeches are missing from the dataset (1962 and 1995).
    The dataset has 79 rows but those two years are missing data.

    Args:
        df: Filtered corpus DataFrame
        total_speeches: Total number of speeches in full dataset (default: 77)

    Returns:
        String describing inclusion count (e.g., "75 of 77 speeches included.")
    """
    # Count only speeches with actual data (excluding 1962 and 1995)
    n = len(df)

    if n == total_speeches:
        return f"{total_speeches} speeches included."
    else:
        return f"{n} of {total_speeches} speeches included."
