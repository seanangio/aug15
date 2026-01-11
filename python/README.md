# Indian Independence Day Speeches - Streamlit App

A Python port of the R Shiny app for analyzing Indian Independence Day speeches delivered annually on August 15th since 1947.

## Features

This interactive web application provides visualizations including:

- **Speech Length**: Word count trends over time
- **Most Frequent Words**: Top words after removing stopwords (with optional faceting)
- **Most Important Words**: TF-IDF analysis to identify distinctive words by year
- **+/- Sentiment Words**: Most frequent positive and negative words using NLTK opinion lexicon
- **Net Sentiment**: Difference between positive and negative word counts over time
- **Specific Word Trend**: Track any word's frequency across speeches

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

## Installation

### 1. Clone or Navigate to Repository

```bash
cd /path/to/aug15/python
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

On macOS/Linux:
```bash
source venv/bin/activate
```

On Windows:
```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. NLTK Data (Auto-downloaded)

The app will automatically download required NLTK data (stopwords and opinion lexicon) on first run. If you encounter issues, you can manually download:

```python
import nltk
nltk.download('stopwords')
nltk.download('opinion_lexicon')
```

## Running the App

### Start the Streamlit Server

```bash
streamlit run app.py
```

The app will open automatically in your default web browser at `http://localhost:8501`.

### Using the App

1. **Filters (Sidebar)**:
   - Adjust year range with the slider
   - Select Prime Ministers to include
   - Select political parties to include
   - Click "Reset All Inputs" to restore defaults

2. **Plot Options**:
   - Choose plot type from dropdown
   - Conditional inputs appear based on plot type:
     - Number of words (for word frequency/importance plots)
     - Facet variable (for breaking down by year/PM/party)
     - Word to track (for specific word trend)

3. **Main Display**:
   - Interactive plot with hover tooltips
   - Explanation text below each plot

## Project Structure

```
python/
├── app.py                   # Main Streamlit application
├── utils/
│   ├── __init__.py
│   ├── data_prep.py        # Data loading and filtering
│   ├── text_analysis.py    # Tokenization, TF-IDF, sentiment analysis
│   └── plotting.py         # Plotly visualization functions
├── data/
│   └── corpus.csv          # Symlink to ../inst/final_csv/corpus.csv
├── tests/
│   ├── __init__.py
│   ├── test_data_prep.py
│   └── test_text_analysis.py
├── requirements.txt        # Python dependencies
├── .python-version        # Python version specification
├── .gitignore            # Python-specific ignores
└── README.md             # This file
```

## Running Tests

The project includes unit tests using pytest:

```bash
# Install pytest if not already installed
pip install pytest

# Run all tests
pytest tests/

# Run with verbose output
pytest -v tests/

# Run specific test file
pytest tests/test_data_prep.py
```

## Technical Details

### Data Processing

- **Tokenization**: Regular expression-based word extraction
- **Stopwords**: NLTK English stopword list
- **TF-IDF**: scikit-learn's `TfidfVectorizer`
- **Sentiment**: NLTK opinion lexicon (positive/negative word lists)

### Visualization

- All plots use Plotly for interactivity
- Color scheme extracted from ggplot2 defaults to match R Shiny app:
  - BJP: #F8766D (red-ish)
  - INC: #7CAE00 (green)
  - Janata Dal: #00BFC4 (cyan)
  - Janata Party: #C77CFF (purple)

### Performance

- Corpus data is cached using `@st.cache_data`
- Text processing is performed on-demand based on selected filters

## Differences from R Shiny App

This Python port aims to replicate the R Shiny app as closely as possible, with these minor differences:

1. **Sentiment Lexicon**: Uses NLTK opinion lexicon instead of Bing lexicon (both provide positive/negative word classifications)
2. **Reset Button**: Simplified to "Clear Filters" functionality rather than full session state management
3. **Styling**: Close approximation of R Shiny theme using Streamlit's CSS customization

## Troubleshooting

### Port Already in Use

If port 8501 is already in use:

```bash
streamlit run app.py --server.port 8502
```

### NLTK Download Issues

If auto-download fails, manually download required data:

```python
python -c "import nltk; nltk.download('stopwords'); nltk.download('opinion_lexicon')"
```

### Data File Not Found

Ensure the symlink is correctly set up:

```bash
ls -la data/corpus.csv
# Should show: corpus.csv -> ../../inst/final_csv/corpus.csv
```

If broken, recreate:

```bash
rm data/corpus.csv
ln -s "../../inst/final_csv/corpus.csv" "data/corpus.csv"
```

## Development

### Code Style

The project follows Python best practices:

- PEP 8 formatting (can use `black` for auto-formatting)
- Type hints for function signatures
- Google-style docstrings

### Adding Features

1. Data processing functions → `utils/data_prep.py` or `utils/text_analysis.py`
2. New plot types → `utils/plotting.py`
3. UI changes → `app.py`

### Formatting Code

```bash
# Install black
pip install black

# Format all Python files
black python/
```

## Credits

- Original R package and Shiny app: [github.com/seanangio/aug15](https://github.com/seanangio/aug15)
- Python port: Streamlit implementation with equivalent functionality

## License

Same as parent repository.
