# Quick Start Guide

## Running the Streamlit App

### First Time Setup

1. **Navigate to the python directory**:
   ```bash
   cd /path/to/aug15/python
   ```

2. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

   You should see `(venv)` appear in your terminal prompt.

3. **Run the app**:
   ```bash
   streamlit run app.py
   ```

4. **Access the app**:
   - The app will automatically open in your browser
   - Or manually visit: `http://localhost:8501`

### Subsequent Runs

After the first setup, you only need:

```bash
cd /path/to/aug15/python
source venv/bin/activate
streamlit run app.py
```

### Stopping the App

Press `Ctrl+C` in the terminal to stop the server.

### Deactivating Virtual Environment

When you're done:
```bash
deactivate
```

## Running Tests

```bash
cd /path/to/aug15/python
source venv/bin/activate
pytest tests/ -v
```

## Troubleshooting

### Port Already in Use

If you see an error about port 8501:
```bash
streamlit run app.py --server.port 8502
```

### Data File Not Found

Check the symlink:
```bash
ls -la data/corpus.csv
```

Should show: `corpus.csv -> ../../inst/final_csv/corpus.csv`

If broken, recreate:
```bash
rm data/corpus.csv
ln -s "../../inst/final_csv/corpus.csv" "data/corpus.csv"
```

### NLTK Data Missing

The app auto-downloads NLTK data, but if it fails:
```python
python3 -c "import nltk; nltk.download('stopwords'); nltk.download('opinion_lexicon')"
```

## Using the App

### Filters (Left Sidebar)
1. **Years**: Drag slider to select year range
2. **Prime Ministers**: Click to select/deselect PMs
3. **Parties**: Click to select/deselect parties
4. **Reset Button**: Click to restore all defaults

### Plot Types
1. Select plot type from dropdown
2. Additional options appear based on selection:
   - **Number of Words**: How many words to show in frequency plots
   - **Facet Variable**: Break down by year, PM, or party
   - **Word to Count**: Enter any word to track its frequency

### Interactive Features
- Hover over plot points to see details
- Pan and zoom on plots (using Plotly toolbar)
- Toggle legend items by clicking them

## Example Workflow

1. Start with default settings (all years, all PMs, all parties)
2. View "Speech Length" to see overall trends
3. Switch to "Most Important Words" to see TF-IDF by year
4. Filter to just recent years (2000-2025) and one party
5. Try "Specific Word Trend" with words like:
   - "freedom"
   - "democracy"
   - "development"
   - "kashmir"
   - "pakistan"

## Performance Tips

- First load takes ~5-10 seconds (data loading + NLTK setup)
- Subsequent plot changes are faster (< 2 seconds)
- Filtering is near-instant due to caching
- TF-IDF calculation is the slowest operation

## Comparing with R Shiny App

To run both apps side-by-side:

1. **Terminal 1 - R Shiny**:
   ```bash
   cd /path/to/aug15
   R -e "shiny::runApp('inst/examples/analysis_app', port=3838)"
   ```
   Visit: `http://localhost:3838`

2. **Terminal 2 - Streamlit**:
   ```bash
   cd /path/to/aug15/python
   source venv/bin/activate
   streamlit run app.py
   ```
   Visit: `http://localhost:8501`

Now you can compare features, styling, and performance directly!
