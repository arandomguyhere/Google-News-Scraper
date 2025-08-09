import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

# --------- Config ----------
LATEST_JSON = Path("data/latest_news.json")
DOCS_DIR = Path("docs")
DEBUG_HTML = DOCS_DIR / "index.html"
FEED_JSON = DOCS_DIR / "feed.json"
MAX_PER_CATEGORY = 6
SIMILARITY_THRESHOLD = 0.7
# ---------------------------

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def parse_date(val: str | None) -> datetime | None:
    """Parse many date formats -> aware UTC datetime if possible."""
    if not val:
        return None
    try:
        # Try ISO first
        dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        pass
    # Try a few common news formats
    for fmt in ("%Y-%m-%d %H:%M:%S", "%a, %d %b %Y %H:%M:%S %Z", "%d %b %Y %H:%M:%S %Z"):
        try:
            dt = datetime.strptime(val, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except Exception:
            continue
    return None

def human_age(dt: datetime | None) -> str:
    if not dt:
        return ""
    delta = now_utc() - dt
    s = int(delta.total_seconds())
    if s < 60:
        return f"{s}s ago"
    m = s // 60
    if m < 60:
        return f"{m}m ago"
    h = m // 60
    if h < 24:
        return f"{h}h ago"
    d = h // 24
    return f"{d}d ago"

def remove_duplicate_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Simple title-similarity dedupe."""
    if not articles:
        return []
    unique: List[Dict[str, Any]] = []
    seen_titles: List[str] = []
    for a in articles:
        title = (a.get("Title") or "").strip().lower()
        if not title:
            continue
        title_words = set(title.split())
        dup = False
        for seen in seen_titles:
            seen_words = set(seen.split())
            if not title_words or not seen_words:
                continue
            sim = len(title_words & seen_words) / max(len(title_words), len(seen_words))
            if sim > SIMILARITY_THRESHOLD:
                dup = True
                break
        if not dup:
            seen_titles.append(title)
            unique.append(a)
    return unique

def normalize_item(a: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map your scraper fields -> UI feed fields.
    Expected input keys (best-effort): Title, Link, Source, Published, Summary, Category, Image
    """
    published_dt = parse_date(a.get("Published"))
    topics = []
    # Use Category as a topic; also try to infer a couple of common tags from title keywords (optional)
    cat = (a.get("Category") or "General Cyber").strip()
    if cat:
        topics.append(cat)
    title_l = (a.get("Title") or "").lower()
    if "ransomware" in title_l: topics.append("Ransomware")
    if "zero-day" in title_l or "zero day" in title_l or "cve-" in title_l: topics.append("Vulnerabilities")
    if "apt" in title_l: topics.append("APT")
    if "vpn" in title_l: topics.append("VPN")

    # Choose an image if your scraper provides one, else None
    image = a.get("Image")
    if isinstance(image, str) and image.strip() == "":
        image = None

    return {
        "title": a.get("Title") or "Untitled",
        "url": a.get("Link") or "#",
        "source": a.get("Source") or "Unknown",
        "published": published_dt.isoformat().replace("+00:00", "Z") if published_dt else None,
        "published_human": human_age(published_dt),
        "summary": a.get("Summary") or "",
        "image": image,
        "topics": list(dict.fromkeys(topics)),  # de-dup while preserving order
        # Optionally set priority: True for very recent or by category rule
        "priority": bool(published_dt and (now_utc() - published_dt).total_seconds() < 6 * 3600),
    }

def write_atomic(path: Path, content: str):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)

def generate_html_and_feed() -> int:
    print("🔍 DEBUG: Starting HTML + feed generation...")
    print(f"🔍 DEBUG: Looking for file: {LATEST_JSON}")
    print(f"🔍 DEBUG: File exists: {LATEST_JSON.exists()}")
    if LATEST_JSON.exists():
        print(f"🔍 DEBUG: File size: {LATEST_JSON.stat().st_size} bytes")

    # Load JSON
    try:
        news_data = json.loads(LATEST_JSON.read_text(encoding="utf-8"))
        if isinstance(news_data, dict) and "items" in news_data:
            # support an alternative shape { items: [...] }
            news_data = news_data["items"]
        print(f"🔍 DEBUG: Successfully loaded JSON with {len(news_data)} articles")
        if news_data:
            first = news_data[0]
            print("🔍 DEBUG: First article sample:")
            for k, v in list(first.items())[:8]:
                print(f"    {k}: {str(v)[:100]}...")
    except FileNotFoundError:
        print("❌ DEBUG: JSON file not found!")
        news_data = []
    except json.JSONDecodeError as e:
        print(f"❌ DEBUG: JSON decode error: {e}")
        news_data = []
    except Exception as e:
        print(f"❌ DEBUG: Unexpected error loading JSON: {e}")
        news_data = []

    # Dedupe
    unique_articles = remove_duplicate_articles(news_data)
    print(f"🔍 DEBUG: After deduplication: {len(unique_articles)} articles")

    # Normalize for UI feed
    normalized = [normalize_item(a) for a in unique_articles]

    # Group for debug HTML
    categories: Dict[str, List[Dict[str, Any]]] = {}
    for n in normalized:
        cat = (n.get("topics")[0] if n.get("topics") else "General Cyber") or "General Cyber"
        categories.setdefault(cat, []).append(n)

    # Sort each category newest first
    for cat, arr in categories.items():
        arr.sort(key=lambda x: parse_date(x.get("published")) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)

    print(f"🔍 DEBUG: Categories found: {list(categories.keys())}")
    for cat, arr in categories.items():
        print(f"    {cat}: {len(arr)} articles")

    # Ensure docs/
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # --------- Write feed.json for React page ----------
    feed = {
        "generated_at": now_utc().isoformat().replace("+00:00", "Z"),
        "items": sorted(
            normalized,
            key=lambda x: (x.get("priority", False), parse_date(x.get("published")) or datetime.min.replace(tzinfo=timezone.utc)),
            reverse=True,
        )
    }
    write_atomic(FEED_JSON, json.dumps(feed, ensure_ascii=False, indent=2))
    print(f"🔍 DEBUG: Wrote {FEED_JSON} with {len(feed['items'])} items")

    # --------- Build DEBUG HTML (your existing visual brief) ----------
    date_formatted = now_utc().astimezone().strftime("%B %d, %Y")
    html_parts = [f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DEBUG: Cyber Intelligence Brief - {date_formatted}</title>
<style>
body{{font-family:Arial,sans-serif;margin:20px;background:#f5f5f5}}
.container{{max-width:900px;margin:0 auto;background:white;padding:20px;border-radius:8px}}
.debug-info{{background:#e8f4fd;padding:15px;border-radius:6px;margin-bottom:20px;border-left:4px solid #007acc}}
.article{{border:1px solid #ddd;margin:10px 0;padding:15px;border-radius:6px}}
.article-title{{font-weight:bold;color:#007acc;margin-bottom:8px}}
.article-meta{{color:#666;font-size:0.9em;margin-bottom:10px}}
.category-header{{background:#007acc;color:white;padding:10px;margin:20px 0 10px 0;border-radius:4px}}
.small{{font-size:.85em;color:#555}}
</style>
</head>
<body>
<div class="container">
  <h1>🔍 DEBUG: Bob's Brief</h1>
  <p><strong>Debug Mode:</strong> {date_formatted}</p>
  <div class="debug-info">
    <h3>🔍 Debug Information</h3>
    <p><strong>Total articles loaded from JSON:</strong> {len(news_data)}</p>
    <p><strong>Unique after dedupe:</strong> {len(unique_articles)}</p>
    <p><strong>Categories found:</strong> {len(categories)}</p>
    <p><strong>Generated at:</strong> {now_utc().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    <p class="small">Also wrote <code>{FEED_JSON.as_posix()}</code> for the THN-style front page.</p>
  </div>
"""]

    if categories:
        for category, articles in categories.items():
            html_parts.append(f'<div class="category-header">📂 {category} ({len(articles)} articles)</div>')
            for art in articles[:MAX_PER_CATEGORY]:
                title = art.get("title", "No Title")
                source = art.get("source", "Unknown Source")
                published = art.get("published")
                link = art.get("url", "#")
                when = art.get("published_human") or (published or "")
                html_parts.append(f"""
<div class="article">
  <div class="article-title"><a href="{link}" target="_blank" rel="noopener">{title}</a></div>
  <div class="article-meta">{source} | {when}</div>
</div>
""")
    else:
        html_parts.append("""
<div class="debug-info">
  <h3>❌ No Categories Found</h3>
  <p>The JSON file was loaded but no categories were processed.</p>
</div>
""")

    html_parts.append("""
</div>
<script>
console.log('DEBUG: HTML page loaded');
</script>
</body>
</html>""")

    write_atomic(DEBUG_HTML, "".join(html_parts))
    print(f"🔍 DEBUG: Wrote {DEBUG_HTML}")

    return len(normalized)

if __name__ == "__main__":
    count = generate_html_and_feed()
    print(f"✅ Done. Items in feed: {count}")
