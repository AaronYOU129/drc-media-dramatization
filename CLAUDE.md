# Project Overview

News media analysis project studying **dramatization** in international coverage of the **Democratic Republic of Congo (DRC)**, comparing Guardian and Reuters.

## Directory Structure

```
salience_news/
├── code/
│   ├── scraping/          # Data collection (API + web)
│   ├── cleaning/          # Text preprocessing
│   └── analysis/          # Dramatization measurement & comparison
├── data/
│   ├── raw/               # Unprocessed scraped data
│   ├── processed/         # Cleaned data
│   └── final/             # Analysis-ready datasets
└── README.md
```

## Data Pipeline

1. **Data Collection** — Guardian API (925 articles), Reuters web scraping (340 conflict articles)
2. **Text Preprocessing** — Cleaning, tokenization, conflict keyword filtering
3. **Dramatization Measurement** — Four dictionaries, z-scores, PCA → dramatization index
4. **Comparative Analysis** — Guardian vs Reuters; pre/post M23 escalation
5. **Experimental Materials** — High-dramatization templates, balanced condition, comment stimuli
6. **Experiment Data Collection** *(planned)* — Prolific recruitment
7. **Experiment Analysis** *(planned)* — R1–R4 regressions

## Key Scripts

- `code/scraping/gdn_api_2018_2024.py` — Guardian API scraper
- `code/scraping/rtr_web_2021_2025_part1.py` & `part2.py` — Reuters web scrapers

## Tech Stack

- **Selenium WebDriver** for web scraping
- **Requests** for API access
- **Pandas** for data processing

## Naming Conventions

- Sources: `gdn` (Guardian), `rtr` (Reuters), `gdelt` (GDELT)
- Methods: `api` (API access), `web` (web-scraped)
- Date ranges: `YYYY_YYYY`

---

# Coding Principles

## Script Header

Every script must begin with a header comment in this format:

```
Purpose:    What the script does and why the approach was chosen.
Inputs:     Exact file paths and descriptions of each input.
Outputs:    Generated files and their locations.
Key Steps:  High-level logical workflow (not repeating function names).
How to Run: Command to execute the script.
```

The Purpose field must explain **why** key methodological choices were made, not just restate what the code does. A reader should understand the script within 30 seconds by reading the header alone.

## Code Organization

- Input and output paths must be explicit and consistent across scripts.
- Scripts should reflect the research pipeline: Data → Processing → Estimation → Output.
- Extract shared logic into reusable modules; avoid code duplication.
- Keep functions small with one clear responsibility. High-level functions describe workflow; low-level functions handle details.
- Separate loading, cleaning, computation, plotting, and exporting when they are meaningfully distinct.

## Style

- Use early returns to reduce nesting; keep the "happy path" visually obvious.
- Prefer clear, specific names over short abbreviations. Use consistent terminology across the project.
- Comments explain **why**, not **what**. Do not compensate for poor naming with comments.
- Do not over-engineer short, linear code. Refactor only when it improves clarity or responsibility boundaries.
