"""
Streamlit app for analyzing Indian Independence Day speeches.

This app provides interactive visualizations of speeches delivered annually
on August 15th since 1947.
"""

import streamlit as st
from utils.data_prep import load_corpus, filter_corpus, get_current_n
from utils.text_analysis import (
    tokenize_text,
    remove_stopwords,
    calculate_tf_idf,
    calculate_sentiment_words,
    calculate_net_sentiment,
    count_specific_word
)
from utils.plotting import (
    plot_speech_length,
    plot_freq_words,
    plot_tf_idf,
    plot_sentiment_words,
    plot_net_sentiment,
    plot_specific_word_trend,
    get_plot_explanation,
    PLOT_CONFIG
)


# Page configuration
st.set_page_config(
    page_title="Indian Independence Day Speeches",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
st.markdown("""
<style>
hr {
    border-top: 1px solid gray;
    margin: 1em 0;
}

.stButton button {
    width: 100%;
}

/* Match Shiny app styling */
.main .block-container {
    padding-top: 2rem;
}

h1 {
    font-size: 2.5rem;
    font-weight: 600;
}

/* Smaller buttons for All/None selectors */
.stButton button[kind="secondary"] {
    padding: 0.25rem 0.5rem;
    font-size: 0.875rem;
}
</style>
""", unsafe_allow_html=True)


# Initialize session state for filters
if 'initialized' not in st.session_state:
    corpus = load_corpus()
    st.session_state.initialized = True
    st.session_state.default_year_range = (int(corpus['year'].min()), int(corpus['year'].max()))
    st.session_state.default_pms = sorted(corpus['pm'].unique().tolist())
    st.session_state.default_parties = sorted(corpus['party'].unique().tolist())
    st.session_state.default_max_words = 12
    st.session_state.default_facet_var = 'none'
    st.session_state.default_word = 'freedom'


# Title
st.title("Indian Independence Day Speeches")

# Load data
corpus = load_corpus()

# Sidebar
with st.sidebar:
    # Reset button
    if st.button("🔄 Reset All Inputs"):
        st.session_state.year_range = st.session_state.default_year_range
        st.session_state.selected_pms = st.session_state.default_pms
        st.session_state.selected_parties = st.session_state.default_parties
        st.session_state.max_words = st.session_state.default_max_words
        st.session_state.facet_var = st.session_state.default_facet_var
        st.session_state.chosen_word = st.session_state.default_word
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Filter controls
    year_range = st.select_slider(
        "Years",
        options=list(range(int(corpus['year'].min()), int(corpus['year'].max()) + 1)),
        value=st.session_state.get('year_range', st.session_state.default_year_range),
        key='year_range'
    )

    # Prime Ministers selector with select all/none buttons
    pm_col1, pm_col2, pm_col3 = st.columns([2, 1, 1])
    with pm_col1:
        st.markdown("**Prime Ministers**")
    with pm_col2:
        if st.button("All", key="pm_all", use_container_width=True):
            st.session_state.selected_pms = st.session_state.default_pms
            st.rerun()
    with pm_col3:
        if st.button("None", key="pm_none", use_container_width=True):
            st.session_state.selected_pms = []
            st.rerun()

    selected_pms = st.multiselect(
        "Prime Ministers",
        options=sorted(corpus['pm'].unique()),
        default=st.session_state.get('selected_pms', st.session_state.default_pms),
        key='selected_pms',
        label_visibility="collapsed"
    )

    # Parties selector with select all/none buttons
    party_col1, party_col2, party_col3 = st.columns([2, 1, 1])
    with party_col1:
        st.markdown("**Parties**")
    with party_col2:
        if st.button("All", key="party_all", use_container_width=True):
            st.session_state.selected_parties = st.session_state.default_parties
            st.rerun()
    with party_col3:
        if st.button("None", key="party_none", use_container_width=True):
            st.session_state.selected_parties = []
            st.rerun()

    selected_parties = st.multiselect(
        "Parties",
        options=sorted(corpus['party'].unique()),
        default=st.session_state.get('selected_parties', st.session_state.default_parties),
        key='selected_parties',
        label_visibility="collapsed"
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # Plot type selection
    plot_type = st.selectbox(
        "Plot Type",
        options=[
            'Speech Length',
            'Most Frequent Words',
            'Most Important Words',
            '+/- Sentiment Words',
            'Net Sentiment',
            'Specific Word Trend'
        ]
    )

    # Conditional inputs based on plot type
    if plot_type in ['Most Frequent Words', 'Most Important Words', '+/- Sentiment Words']:
        max_words = st.number_input(
            "Number of Words to Include",
            min_value=1,
            value=st.session_state.get('max_words', st.session_state.default_max_words),
            key='max_words'
        )
    else:
        max_words = 12

    if plot_type in ['Most Frequent Words', '+/- Sentiment Words']:
        facet_var = st.selectbox(
            "Facet Variable",
            options=['None', 'Year', 'Prime Minister', 'Party'],
            index=0,
            key='facet_select'
        )
        # Map display names to column names
        facet_map = {
            'None': 'none',
            'Year': 'year',
            'Prime Minister': 'pm',
            'Party': 'party'
        }
        facet_var = facet_map[facet_var]
    else:
        facet_var = 'none'

    if plot_type == 'Specific Word Trend':
        chosen_word = st.text_input(
            "Word to Count",
            value=st.session_state.get('chosen_word', st.session_state.default_word),
            key='chosen_word'
        )
    else:
        chosen_word = 'freedom'

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("[Code & Documentation on GitHub](https://github.com/seanangio/aug15)")


# Main content area
# Filter corpus
if selected_pms and selected_parties:  # Only process if filters are selected
    corpus_filtered = filter_corpus(corpus, year_range, selected_pms, selected_parties)

    # Display current count
    st.markdown(f"*{get_current_n(corpus_filtered)}*")
    st.markdown("*1962 and 1995 are missing from the data set.*")

    # Process data based on plot type with spinner
    with st.spinner('Generating plot...'):
        if plot_type == 'Speech Length':
            corpus_tidy = tokenize_text(corpus_filtered)
            fig = plot_speech_length(corpus_tidy)

        elif plot_type == 'Most Frequent Words':
            corpus_tidy = tokenize_text(corpus_filtered)
            corpus_nonstop = remove_stopwords(corpus_tidy)
            fig = plot_freq_words(corpus_nonstop, facet_var, max_words)

        elif plot_type == 'Most Important Words':
            corpus_tidy = tokenize_text(corpus_filtered)
            corpus_tf_idf = calculate_tf_idf(corpus_tidy)
            fig = plot_tf_idf(corpus_tf_idf, max_words)

        elif plot_type == '+/- Sentiment Words':
            corpus_tidy = tokenize_text(corpus_filtered)
            corpus_nonstop = remove_stopwords(corpus_tidy)
            corpus_sentiment = calculate_sentiment_words(corpus_nonstop)
            fig = plot_sentiment_words(corpus_sentiment, facet_var, max_words)

        elif plot_type == 'Net Sentiment':
            corpus_tidy = tokenize_text(corpus_filtered)
            corpus_nonstop = remove_stopwords(corpus_tidy)
            corpus_sentiment = calculate_sentiment_words(corpus_nonstop)
            corpus_net = calculate_net_sentiment(corpus_sentiment)
            fig = plot_net_sentiment(corpus_net)

        elif plot_type == 'Specific Word Trend':
            corpus_tidy = tokenize_text(corpus_filtered)
            corpus_word = count_specific_word(corpus_tidy, chosen_word)
            fig = plot_specific_word_trend(corpus_word, chosen_word)

        # Display plot
        st.plotly_chart(fig, use_container_width=True, config=PLOT_CONFIG)

    # Display explanation
    explanation = get_plot_explanation(plot_type)
    st.info(explanation)

else:
    st.warning("Please select at least one Prime Minister and one Party to view visualizations.")
