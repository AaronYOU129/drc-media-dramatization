# Project Overview

This is a **news media analysis project** studying media coverage and **dramatization** of the **Democratic Republic of Congo (DRC)** from major international outlets (Guardian, Reuters).

## Directory Structure
```
salience_news/
├── code/
│   ├── scraping/          # Pipeline 1: Data collection
│   ├── cleaning/          # Pipeline 2: Text preprocessing
│   └── analysis/          # Pipelines 3-4: Analysis
├── data/
│   ├── raw/               # Unprocessed scraped data
│   ├── processed/         # Cleaned data
│   └── final/             # Final datasets
└── README.md
```

## Data Pipeline
1. **Data Collection** - Guardian API (925 articles), Reuters (340 conflict articles)
2. **Text Preprocessing** - Clean text, tokenization, conflict keyword filtering
3. **Dramatization Measurement** - Four dictionaries, z-scores, PCA for dramatization index
4. **Comparative Analysis** - Guardian vs Reuters, Pre/post M23 analysis
5. **Experimental Materials** - High-dramatization templates, balanced condition, comment stimuli
6. **Experiment Data Collection** *(future)* - Prolific recruitment
7. **Experiment Analysis** *(future)* - R1-R4 regressions

## Key Scripts
- `code/scraping/gdn_api_2018_2024.py` - Guardian API scraper
- `code/scraping/rtr_web_2021_2025_part1.py` & `part2.py` - Reuters web scrapers

## Tech Stack
- Selenium WebDriver for web scraping
- Requests for API access
- Pandas for data processing

## Data Naming Convention
- Source codes: `gdn` (Guardian), `rtr` (Reuters), `gdelt` (GDELT)
- Method codes: `api` (API access), `web` (web-scraped)
- Date format: `YYYY_YYYY` for ranges
