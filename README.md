# Media Coverage and Public Perception of DRC

Analyzing Guardian and Reuters articles on the Democratic Republic of Congo.

## Project Structure

```
salience_news/
├── code/
│   ├── scraping/          # Data collection scripts
│   ├── cleaning/          # Data cleaning scripts
│   └── analysis/          # Analysis scripts
├── data/
│   ├── raw/               # Unprocessed scraped data
│   ├── processed/         # Cleaned data
│   └── final/             # Final datasets
├── output/
│   └── figures/           # Generated figures (PDFs)
└── README.md
```

## Data Pipeline

### Pipeline 1: Data Collection
- Guardian API data collection (925 articles, 2018-2024)
- Reuters data collection (340 conflict articles)
- Store raw data with metadata (date, headline, full text, URL)

| Script | Source | Method | Output |
|--------|--------|--------|--------|
| `gdn_api_2018_2024.py` | Guardian | API | `data/processed/gdn_api_2018_2024.csv` |
| `rtr_web_2021_2025_part1.py` | Reuters | Web scraping | `data/raw/rtr_web_2021_2025.csv` |
| `rtr_web_2021_2025_part2.py` | Reuters | Web scraping | `data/raw/rtr_web_2021_2025_part2.csv` |

### Pipeline 2: Text Preprocessing
- Clean text (remove HTML, normalize whitespace)
- Tokenization
- Identify conflict-related articles using keyword filter

### Pipeline 3: Dramatization Measurement
- Apply four dictionaries (emotional, personalization, narrative, first-person)
- Calculate word counts per 1,000 words
- Compute z-scores for each dimension
- Run PCA to extract dramatization index (PC1)
- LLM validation using DeepSeek (r = 0.652 with PCA index)

| Script | Description | Output |
|--------|-------------|--------|
| `dramatization index.py` | Dictionary-based scoring + PCA | `data/processed/*_conflict_analyzed.csv` |
| `llm_validation.py` | DeepSeek LLM validation | `output/llm_validation_results.csv` |
| `llm_validation_analysis.py` | Correlation analysis | `output/llm_validation_summary.txt` |

### Pipeline 4: Comparative Analysis
- Guardian vs. Reuters comparison (Table 5)
- Pre/post M23 analysis (Tables 6-7)
- Generate Figures 1-4

| Script | Description | Output |
|--------|-------------|--------|
| `comparison.py` | Guardian vs Reuters, pre/post M23 | `output/summary_statistics.csv` |
| `figures.py` | Generate analysis figures | `output/figures/*.pdf` |

### Pipeline 5: Experimental Materials
- Select high-dramatization articles as templates for "Dramatized" condition
- Construct balanced condition from institutional reports
- Design comment stimuli (3 positive, 3 negative)

### Pipeline 6: Experiment Data Collection *(future)*
- Prolific recruitment
- Survey/experiment administration

### Pipeline 7: Experiment Analysis *(future)*
- R1-R4 regressions from Section 3.7

## Setup

1. Install dependencies:
   ```bash
   pip install requests pandas selenium webdriver-manager python-dotenv openai
   ```

2. Create `.env` file from template:
   ```bash
   cp .env.example .env
   ```

3. Add your API keys to `.env`

## Data Sources

- **Guardian API** (2018-2024): ~18k articles with full text
- **Reuters Web** (2021-2025): ~1,500+ articles (title, date, URL)
- **Reuters GDELT** (2018-2023): Historical coverage

## To Do

- [x] Finalize dramatization measures
- [x] Complete text analysis pipeline
- [x] LLM validation of dramatization index
- [ ] Develop experimental design
- [ ] Experiment data collection (Prolific)
- [ ] Experiment analysis (R1-R4 regressions)
