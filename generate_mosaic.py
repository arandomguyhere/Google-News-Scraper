#!/usr/bin/env python3
"""
Bob's Brief - Mosaic Intelligence Generator
Integrates story clustering for organized intelligence output
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from processors.story_correlator import StoryCorrelator, analyze_stories

# --------- Config ----------
LATEST_JSON = Path("data/latest_news.json")
FEED_JSON_INPUT = Path("docs/feed.json")  # Fallback
DOCS_DIR = Path("docs")
HTML_OUTPUT = DOCS_DIR / "index.html"
FEED_JSON = DOCS_DIR / "feed.json"
SIMILARITY_THRESHOLD = 0.3
MAX_CLUSTER_SIZE = 15
# ---------------------------


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def normalize_story(story: Dict) -> Dict:
    """Normalize story fields to consistent format"""
    return {
        'Title': story.get('Title') or story.get('title') or 'Untitled',
        'Link': story.get('Link') or story.get('url') or '#',
        'Source': story.get('Source') or story.get('source') or 'Unknown',
        'Category': story.get('Category') or (story.get('topics', ['General'])[0] if story.get('topics') else 'General'),
        'Published': story.get('Published') or story.get('published') or story.get('published_human') or '',
    }


def load_stories() -> List[Dict]:
    """Load stories from scraper output"""
    data = []

    # Try primary source
    if LATEST_JSON.exists():
        try:
            raw = json.loads(LATEST_JSON.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and "items" in raw:
                raw = raw["items"]
            data = raw
            print(f"Loaded {len(data)} stories from {LATEST_JSON}")
        except Exception as e:
            print(f"Error loading {LATEST_JSON}: {e}")

    # Fallback to feed.json
    if not data and FEED_JSON_INPUT.exists():
        try:
            raw = json.loads(FEED_JSON_INPUT.read_text(encoding="utf-8"))
            if isinstance(raw, dict) and "items" in raw:
                raw = raw["items"]
            data = raw
            print(f"Loaded {len(data)} stories from {FEED_JSON_INPUT}")
        except Exception as e:
            print(f"Error loading {FEED_JSON_INPUT}: {e}")

    # Normalize all stories
    return [normalize_story(s) for s in data]


def detect_early_signals(stories: List[Dict], correlator: StoryCorrelator) -> List[Dict]:
    """
    Detect stories that appear in international sources before US mainstream media.
    These are potential early signals worth watching.
    """
    # Define source tiers
    us_mainstream = {'WSJ', 'NYT', 'Reuters', 'Bloomberg', 'Forbes', 'TechCrunch', 'Wired'}
    international = {'SCMP', 'Korea Times', 'SMH', 'France24', 'Kyiv Independent',
                    'Red Hot Cyber', 'Freebuf', 'WION News', 'Chosun', 'New Straits Times'}
    threat_intel = {'Mandiant', 'CrowdStrike', 'Unit 42', 'Kaspersky', 'SentinelOne',
                   'Trend Micro', 'Elastic Security Labs', 'Huntress'}

    # Track entities and their source coverage
    entity_sources = defaultdict(lambda: {'international': [], 'threat_intel': [], 'us_msm': []})

    for story in stories:
        source = story.get('Source', '')
        text = f"{story.get('Title', '')} {story.get('Category', '')}"
        entities = correlator.extract_entities(text)

        # Flatten entities
        all_entities = set()
        for entity_set in entities.values():
            all_entities.update(entity_set)

        for entity in all_entities:
            if any(s in source for s in international):
                entity_sources[entity]['international'].append(story)
            elif any(s in source for s in threat_intel):
                entity_sources[entity]['threat_intel'].append(story)
            elif any(s in source for s in us_mainstream):
                entity_sources[entity]['us_msm'].append(story)

    # Find entities with international/threat intel coverage but limited US MSM
    early_signals = []
    for entity, coverage in entity_sources.items():
        intl_count = len(coverage['international'])
        intel_count = len(coverage['threat_intel'])
        msm_count = len(coverage['us_msm'])

        # Early signal: Multiple international sources, few/no US MSM
        if (intl_count + intel_count >= 2) and msm_count <= 1:
            signal_stories = coverage['international'] + coverage['threat_intel']
            early_signals.append({
                'entity': entity,
                'international_count': intl_count,
                'threat_intel_count': intel_count,
                'us_msm_count': msm_count,
                'stories': signal_stories[:5],
                'signal_strength': intl_count + intel_count - msm_count
            })

    # Sort by signal strength
    early_signals.sort(key=lambda x: x['signal_strength'], reverse=True)
    return early_signals[:10]


def generate_mosaic_html(stories: List[Dict]) -> int:
    """Generate HTML with mosaic intelligence clustering"""
    print(f"Processing {len(stories)} stories...")

    if not stories:
        print("No stories to process")
        return 0

    # Initialize correlator and analyze
    correlator = StoryCorrelator()
    report = correlator.build_intelligence_report(stories, SIMILARITY_THRESHOLD)

    # Detect early signals
    early_signals = detect_early_signals(stories, correlator)

    # Build HTML
    timestamp = now_utc().strftime('%Y-%m-%d %H:%M UTC')
    date_formatted = now_utc().strftime('%B %d, %Y')

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bob's Brief - {date_formatted}</title>
<style>
:root {{
    --primary: #1a1a2e;
    --secondary: #16213e;
    --accent: #0f3460;
    --highlight: #e94560;
    --text: #eaeaea;
    --muted: #888;
    --card-bg: #16213e;
    --border: #0f3460;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--primary);
    color: var(--text);
    line-height: 1.6;
}}
.container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
header {{
    border-bottom: 1px solid var(--border);
    padding: 30px 0;
    margin-bottom: 30px;
}}
h1 {{ font-size: 2em; font-weight: 600; }}
.subtitle {{ color: var(--muted); margin-top: 5px; }}
.stats {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
    margin-bottom: 30px;
}}
.stat {{
    background: var(--card-bg);
    padding: 20px;
    border-radius: 8px;
    border: 1px solid var(--border);
}}
.stat-number {{ font-size: 2em; font-weight: 700; color: var(--highlight); }}
.stat-label {{ color: var(--muted); font-size: 0.85em; text-transform: uppercase; }}
.section {{ margin-bottom: 40px; }}
.section-title {{
    font-size: 1.3em;
    font-weight: 600;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--highlight);
}}
.early-signals {{
    background: linear-gradient(135deg, #1a1a2e 0%, #2d132c 100%);
    border: 1px solid var(--highlight);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 30px;
}}
.signal {{
    padding: 15px 0;
    border-bottom: 1px solid var(--border);
}}
.signal:last-child {{ border-bottom: none; }}
.signal-entity {{ font-weight: 600; color: var(--highlight); }}
.signal-meta {{ color: var(--muted); font-size: 0.85em; margin-top: 5px; }}
.cluster {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 20px;
    overflow: hidden;
}}
.cluster-header {{
    background: var(--accent);
    padding: 15px 20px;
    font-weight: 600;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
.cluster-size {{
    background: var(--highlight);
    color: white;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.85em;
}}
.cluster-entities {{
    padding: 10px 20px;
    background: rgba(15, 52, 96, 0.5);
    font-size: 0.85em;
    color: var(--muted);
}}
.entity-tag {{
    display: inline-block;
    background: var(--primary);
    padding: 2px 8px;
    border-radius: 4px;
    margin: 2px;
    font-size: 0.8em;
}}
.story {{
    padding: 15px 20px;
    border-bottom: 1px solid var(--border);
}}
.story:last-child {{ border-bottom: none; }}
.story-title {{
    color: var(--text);
    text-decoration: none;
    font-weight: 500;
}}
.story-title:hover {{ color: var(--highlight); }}
.story-meta {{
    color: var(--muted);
    font-size: 0.85em;
    margin-top: 5px;
}}
.story-source {{ color: var(--highlight); }}
.connections {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}}
.connection-group {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
}}
.connection-type {{
    font-weight: 600;
    margin-bottom: 15px;
    text-transform: capitalize;
    color: var(--highlight);
}}
.connection-entity {{
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
}}
.connection-entity:last-child {{ border-bottom: none; }}
.connection-count {{
    background: var(--accent);
    padding: 2px 10px;
    border-radius: 10px;
    font-size: 0.85em;
}}
footer {{
    border-top: 1px solid var(--border);
    padding: 20px 0;
    margin-top: 40px;
    color: var(--muted);
    font-size: 0.85em;
    text-align: center;
}}
</style>
</head>
<body>
<div class="container">
    <header>
        <h1>Bob's Brief</h1>
        <div class="subtitle">Cyber Intelligence Mosaic - {date_formatted}</div>
    </header>

    <div class="stats">
        <div class="stat">
            <div class="stat-number">{report['summary']['total_stories']}</div>
            <div class="stat-label">Stories</div>
        </div>
        <div class="stat">
            <div class="stat-number">{report['summary']['story_clusters']}</div>
            <div class="stat-label">Clusters</div>
        </div>
        <div class="stat">
            <div class="stat-number">{report['summary']['connection_points']}</div>
            <div class="stat-label">Connections</div>
        </div>
        <div class="stat">
            <div class="stat-number">{len(early_signals)}</div>
            <div class="stat-label">Early Signals</div>
        </div>
    </div>
"""

    # Early Signals Section
    if early_signals:
        html += """
    <div class="section early-signals">
        <div class="section-title">Early Signals</div>
        <p style="color: var(--muted); margin-bottom: 15px; font-size: 0.9em;">
            Stories gaining traction in international/threat intel sources before US mainstream coverage.
        </p>
"""
        for signal in early_signals[:5]:
            sources = f"{signal['international_count']} intl, {signal['threat_intel_count']} intel"
            if signal['us_msm_count'] > 0:
                sources += f", {signal['us_msm_count']} MSM"
            html += f"""
        <div class="signal">
            <div class="signal-entity">{signal['entity']}</div>
            <div class="signal-meta">{sources}</div>
        </div>
"""
        html += "    </div>\n"

    # Story Clusters Section
    html += """
    <div class="section">
        <div class="section-title">Story Clusters</div>
"""

    for i, cluster in enumerate(report['clusters'][:20], 1):
        if cluster['size'] < 2:
            continue

        # Get shared entities for this cluster
        cluster_texts = [f"{s.get('title', '')} {s.get('category', '')}" for s in cluster['stories']]
        shared_entities = set()
        for text in cluster_texts:
            entities = correlator.extract_entities(text)
            for ent_set in entities.values():
                shared_entities.update(ent_set)

        # Limit to top entities
        top_entities = list(shared_entities)[:8]

        html += f"""
        <div class="cluster">
            <div class="cluster-header">
                <span>Cluster {i}</span>
                <span class="cluster-size">{cluster['size']} stories</span>
            </div>
"""
        if top_entities:
            html += f"""
            <div class="cluster-entities">
                {''.join(f'<span class="entity-tag">{e}</span>' for e in top_entities)}
            </div>
"""
        for story in cluster['stories']:
            html += f"""
            <div class="story">
                <a href="{story.get('link', '#')}" target="_blank" class="story-title">{story.get('title', 'Untitled')}</a>
                <div class="story-meta">
                    <span class="story-source">{story.get('source', 'Unknown')}</span>
                    {' - ' + story.get('category', '') if story.get('category') else ''}
                </div>
            </div>
"""
        html += "        </div>\n"

    html += "    </div>\n"

    # Connections Section
    html += """
    <div class="section">
        <div class="section-title">Key Connections</div>
        <div class="connections">
"""

    for entity_type, entities in report['connections'].items():
        if not entities:
            continue
        html += f"""
            <div class="connection-group">
                <div class="connection-type">{entity_type.replace('_', ' ')}</div>
"""
        for name, data in list(entities.items())[:8]:
            html += f"""
                <div class="connection-entity">
                    <span>{name}</span>
                    <span class="connection-count">{data['mention_count']}</span>
                </div>
"""
        html += "            </div>\n"

    html += """
        </div>
    </div>
"""

    # Footer
    html += f"""
    <footer>
        Generated: {timestamp} | {report['summary']['total_stories']} stories analyzed
    </footer>
</div>
</body>
</html>
"""

    # Write files
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Wrote: {HTML_OUTPUT}")

    # Write feed.json with clustered data
    feed = {
        'generated_at': now_utc().isoformat(),
        'summary': report['summary'],
        'early_signals': early_signals,
        'clusters': report['clusters'][:20],
        'connections': report['connections'],
        'timeline': report['timeline'][:50]
    }

    with open(FEED_JSON, 'w', encoding='utf-8') as f:
        json.dump(feed, f, indent=2, ensure_ascii=False)
    print(f"Wrote: {FEED_JSON}")

    return report['summary']['total_stories']


def main():
    print("="*60)
    print("BOB'S BRIEF - MOSAIC INTELLIGENCE GENERATOR")
    print("="*60)

    stories = load_stories()

    if not stories:
        print("No stories found in data/latest_news.json")
        return

    count = generate_mosaic_html(stories)
    print(f"\nProcessed {count} stories into mosaic intelligence report")


if __name__ == "__main__":
    main()
