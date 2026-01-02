# Bob's Daily Brief

Automated cybersecurity news aggregation with mosaic intelligence clustering.

[![Scraping Status](https://github.com/arandomguyhere/Google-News-Scraper/actions/workflows/scrape-news.yml/badge.svg)](https://github.com/arandomguyhere/Google-News-Scraper/actions/workflows/scrape-news.yml)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)](https://arandomguyhere.github.io/Google-News-Scraper/)

## What It Does

Continuously monitors 40+ cybersecurity news sources, clusters related stories to reveal the bigger picture, and deploys a live intelligence brief via GitHub Pages.

**Live Brief**: [arandomguyhere.github.io/Google-News-Scraper](https://arandomguyhere.github.io/Google-News-Scraper/)

## Features

- **Multi-source scraping**: 126 targeted search queries across mainstream media, security publications, threat intel vendors, and international sources
- **Mosaic intelligence**: Clusters related stories using multi-dimensional entity matching (countries, threat actors, sectors, techniques)
- **Threat actor tracking**: 60+ named APT groups, ransomware gangs, and nation-state actors
- **Early signal detection**: Surfaces stories gaining traction internationally before US mainstream coverage
- **Historical archives**: Timestamped snapshots for trend analysis

## How It Works

```
scraper.py              126 queries (with when:24h freshness), 350+ stories per run
    |
    v
generate_mosaic.py      Story clustering + entity extraction
    |
    +-- StoryCorrelator
    |     - Entity extraction (regex patterns)
    |     - Multi-dimensional matching (2+ dimensions required)
    |     - TF-IDF word overlap scoring
    |
    v
docs/index.html         Clustered intelligence brief
docs/feed.json          Structured data (clusters, connections, timeline)
```

## Schedule

- Every 6 hours: `0 */6 * * *`
- Weekday mornings: `0 9 * * 1-5`
- Manual: GitHub Actions workflow dispatch

## Repository Structure

```
.
├── scraper.py              # Main scraping engine
├── generate_mosaic.py      # Mosaic intelligence generator
├── requirements.txt        # Python dependencies
├── src/
│   └── processors/
│       ├── story_correlator.py   # Clustering engine
│       └── nlp_processor.py      # NLP utilities (spaCy optional)
├── data/                   # Scraper output (gitignored)
├── docs/                   # GitHub Pages content
│   ├── index.html          # Live newsletter
│   └── feed.json           # Clustered data
└── archives/               # Historical snapshots
```

## Tracked Entities

### Threat Actors (60+)

| Origin | Groups |
|--------|--------|
| Chinese | Salt/Volt/Flax Typhoon, Mustang Panda, Winnti, Hafnium, APT1/10/27/40/41 |
| Russian | Fancy/Cozy Bear, Sandworm, Turla, Star/Midnight Blizzard, APT28/29 |
| North Korean | Lazarus, Kimsuky, Andariel, BlueNoroff, APT37/38 |
| Iranian | Charming Kitten, MuddyWater, OilRig, Mint/Peach Sandstorm, APT33/34/35 |
| Ransomware | LockBit, BlackCat/ALPHV, Clop, Akira, Rhysida, Black Basta, Play |
| Financial | FIN7/11/12, Scattered Spider, LAPSUS$ |

### Other Patterns

- **Countries**: China, Russia, Iran, North Korea, Ukraine, Taiwan, Israel, + 10 more
- **Sectors**: Healthcare, financial, telecom, energy, defense, government, aerospace
- **Techniques**: Phishing, lateral movement, C2, credential stuffing, living off the land
- **Vulnerabilities**: CVE patterns, zero-day, RCE, privilege escalation

## Clustering Algorithm

Stories are grouped when they share 2+ entity dimensions:

```
Example: "China APT telecom" + "China APT infrastructure"
  - Shared: countries (China), threat_actors (APT)
  - Result: Clustered together

Example: "China scams" + "China rare earths"
  - Shared: countries only (China)
  - Result: NOT clustered (only 1 dimension)
```

This prevents overly broad groupings while connecting genuinely related stories.

## Dependencies

```
requests>=2.28.0
beautifulsoup4>=4.12.0
pandas>=2.0.0
lxml>=4.9.0
scikit-learn>=1.3.0
numpy>=1.20.0,<2.0.0
```

Optional: `spacy` with `en_core_web_sm` for enhanced NER (falls back to regex)

## Setup

1. Fork/clone the repository
2. Enable GitHub Actions
3. Configure GitHub Pages (source: GitHub Actions)
4. Run workflow manually or wait for scheduled run

## Debug Mode

Enable via workflow dispatch for:
- Detailed scraper logs
- Extended artifact retention
- Additional diagnostics

## Data Retention

| Type | Retention |
|------|-----------|
| Repository data | Permanent (git) |
| GitHub Pages | Until next deployment |
| Metrics artifacts | 365 days |
| Archives | 90 days |
| Debug logs | 7 days |

---

*Powered by GitHub Actions and mosaic intelligence clustering*
