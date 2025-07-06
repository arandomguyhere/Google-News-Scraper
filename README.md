# 🔒 Cyber Intelligence Brief

> **Automated cybersecurity news aggregation and intelligence reporting system**

[![Scraping Status](https://github.com/your-username/your-repo-name/actions/workflows/scrape-news.yml/badge.svg)](https://github.com/your-username/your-repo-name/actions/workflows/scrape-news.yml)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)](https://your-username.github.io/your-repo-name/)

An automated system that continuously monitors cybersecurity news sources, processes intelligence data, and generates comprehensive reports deployed as a live newsletter.

## 🌟 Features

- **🤖 Fully Automated**: Runs every 6 hours and weekday mornings
- **📰 Multi-Source Scraping**: Aggregates from leading cybersecurity news sources
- **📊 Advanced Analytics**: Tracks metrics, source performance, and trending topics
- **🗂️ Historical Archives**: Maintains timestamped data archives
- **📱 Live Newsletter**: Auto-deployed HTML newsletter via GitHub Pages
- **📈 Performance Tracking**: Query optimization and source reliability metrics
- **🔄 Version Controlled**: All data automatically committed to repository

## 🚀 Live Demo

**🌐 View the latest intelligence brief**: [Live Newsletter](https://your-username.github.io/your-repo-name/)

## 📋 How It Works

### Automation Schedule
- **Every 6 hours**: `0 */6 * * *` - Continuous monitoring
- **Weekday mornings**: `0 9 * * 1-5` - Enhanced coverage during business days
- **Manual trigger**: Available via GitHub Actions interface

### Processing Pipeline

1. **🔍 Data Collection**
   - Multi-source web scraping
   - Content validation and filtering
   - Duplicate detection and removal

2. **📊 Analytics & Metrics**
   - Source performance tracking
   - Category-based analysis
   - Search query optimization
   - Historical trend analysis

3. **🗄️ Archival System**
   - Timestamped data snapshots
   - Long-term data retention
   - Version-controlled storage

4. **📄 Report Generation**
   - HTML newsletter creation
   - Metadata compilation
   - Performance summaries

5. **🚀 Deployment**
   - Automatic GitHub Pages deployment
   - Repository file updates
   - Artifact generation

## 📁 Repository Structure

```
cyber-intelligence-brief/
├── 📄 README.md                    # This file
├── 🔧 .github/workflows/
│   └── scrape-news.yml            # Automation workflow
├── 🐍 scraper.py                  # Main scraping engine
├── 🎨 generate_html.py            # Newsletter generator
├── 📊 metrics_tracker.py          # Analytics and metrics
├── 🗂️ archive_manager.py          # Data archival system
├── 🔍 search_query_tracker.py     # Query optimization
├── 📁 data/                       # Generated data files
│   ├── latest_news.json          # Current news data
│   ├── metrics_tracking.json     # Performance metrics
│   ├── source_statistics.json    # Source analytics
│   ├── category_performance.json # Category insights
│   └── exports/                  # Exported reports
├── 🌐 docs/                       # GitHub Pages content
│   ├── index.html                # Newsletter webpage
│   └── metadata.json             # Deployment info
└── 🗄️ archives/                   # Historical data
    └── YYYYMMDD_HHMMSS/          # Timestamped archives
```

## 📊 Generated Content

### Real-time Data (`data/` folder)
- **`latest_news.json`** - Current cybersecurity news articles
- **`metrics_tracking.json`** - System performance metrics
- **`source_statistics.json`** - Source reliability data
- **`category_performance.json`** - Topic trending analysis
- **`search_query_stats.json`** - Query optimization data

### Reports
- **`metrics_report.txt`** - Comprehensive analytics summary
- **`query_performance_report.txt`** - Search optimization insights

### Archives (`archives/` folder)
Timestamped snapshots for historical analysis and data recovery.

## 🛠️ Setup & Configuration

### Prerequisites
- GitHub repository with Actions enabled
- GitHub Pages enabled in repository settings

### Installation

1. **Fork or clone this repository**
2. **Enable GitHub Actions**:
   - Go to your repository → Actions tab
   - Enable workflows if prompted

3. **Configure GitHub Pages**:
   - Repository Settings → Pages
   - Source: "GitHub Actions"

4. **Customize sources** (optional):
   - Edit `scraper.py` to add/modify news sources
   - Update search queries and filters

### Running the System

**Automatic**: The system runs automatically according to the schedule

**Manual trigger**:
1. Go to Actions tab in your repository
2. Select "Cyber Intelligence Brief - Automated Scraping"
3. Click "Run workflow"
4. Optionally enable debug mode for detailed logs

## 📈 Monitoring & Analytics

### Access Methods

1. **Live Newsletter**: Visit your GitHub Pages URL
2. **Raw Data**: Browse the `data/` folder in your repository
3. **Historical Data**: Check the `archives/` folder
4. **Detailed Reports**: Download artifacts from Actions runs

### Performance Metrics

The system tracks:
- Articles collected per session
- Source reliability and response times
- Content categorization accuracy
- Query performance optimization
- System uptime and error rates

## 🔧 Advanced Configuration

### Debug Mode
Enable debug mode for detailed logging:
- Manual workflow trigger → Enable "debug mode"
- Downloads additional logs and data files
- 7-day artifact retention for troubleshooting

### Customization Options

**Scraping Sources**: Modify `scraper.py`
```python
# Add new sources or modify existing ones
sources = [
    "https://example-cyber-news.com",
    # Add your sources here
]
```

**Report Styling**: Edit `generate_html.py`
```python
# Customize HTML template and styling
template = """
<!-- Your custom HTML template -->
"""
```

**Metrics Tracking**: Configure `metrics_tracker.py`
```python
# Adjust tracking parameters
tracking_config = {
    "retention_days": 90,
    "alert_thresholds": {...}
}
```

## 📊 Data Retention

- **Repository data**: Permanent (version controlled)
- **GitHub Pages**: Live until next deployment
- **Artifacts**: 
  - Metrics reports: 365 days
  - Archives: 90 days
  - Debug logs: 7 days

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with debug mode enabled
5. Submit a pull request

## 📄 License

This project is open source. See the repository for license details.

## 🆘 Support

### Troubleshooting

**Workflow not running?**
- Check Actions are enabled in repository settings
- Verify GITHUB_TOKEN permissions

**No data appearing?**
- Check workflow logs in Actions tab
- Enable debug mode for detailed diagnostics

**GitHub Pages not updating?**
- Verify Pages is configured for "GitHub Actions"
- Check deployment status in Actions tab

### Getting Help

- **Issues**: Open a GitHub issue
- **Discussions**: Use GitHub Discussions
- **Documentation**: Check GitHub Actions documentation

---

**🔄 Last Updated**: Auto-generated during deployment  
**📊 System Status**: [![Build Status](https://github.com/your-username/your-repo-name/actions/workflows/scrape-news.yml/badge.svg)](https://github.com/your-username/your-repo-name/actions)

*Powered by GitHub Actions, Python, and cybersecurity intelligence*
