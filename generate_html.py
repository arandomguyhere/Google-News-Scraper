import json
import os
from datetime import datetime

def generate_html():
    """Generate enhanced visual newsletter with debugging"""
    
    print("🔍 DEBUG: Starting HTML generation...")
    
    # Load the latest news data with debugging
    json_file = "data/latest_news.json"
    print(f"🔍 DEBUG: Looking for file: {json_file}")
    print(f"🔍 DEBUG: File exists: {os.path.exists(json_file)}")
    
    if os.path.exists(json_file):
        file_size = os.path.getsize(json_file)
        print(f"🔍 DEBUG: File size: {file_size} bytes")
    
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            news_data = json.load(f)
        print(f"🔍 DEBUG: Successfully loaded JSON with {len(news_data)} articles")
        
        # Show first article for debugging
        if news_data:
            print(f"🔍 DEBUG: First article sample:")
            first_article = news_data[0]
            for key, value in first_article.items():
                print(f"    {key}: {str(value)[:100]}...")
        
    except FileNotFoundError:
        print("❌ DEBUG: JSON file not found!")
        news_data = []
    except json.JSONDecodeError as e:
        print(f"❌ DEBUG: JSON decode error: {e}")
        news_data = []
    except Exception as e:
        print(f"❌ DEBUG: Unexpected error loading JSON: {e}")
        news_data = []
    
    # Remove duplicates based on title similarity
    unique_articles = remove_duplicate_articles(news_data)
    print(f"🔍 DEBUG: After deduplication: {len(unique_articles)} articles")
    
    # Group articles by category
    categories = {}
    for article in unique_articles:
        category = article.get('Category', 'General Cyber')
        if category not in categories:
            categories[category] = []
        categories[category].append(article)
    
    print(f"🔍 DEBUG: Categories found: {list(categories.keys())}")
    for cat, articles in categories.items():
        print(f"    {cat}: {len(articles)} articles")
    
    # Get current date for newsletter header
    current_date = datetime.now()
    date_formatted = current_date.strftime("%B %d, %Y")
    day_of_year = current_date.timetuple().tm_yday
    
    # Generate HTML - SIMPLIFIED VERSION FOR DEBUGGING
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DEBUG: Cyber Intelligence Brief - {date_formatted}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
        }}
        .debug-info {{
            background: #e8f4fd;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            border-left: 4px solid #007acc;
        }}
        .article {{
            border: 1px solid #ddd;
            margin: 10px 0;
            padding: 15px;
            border-radius: 6px;
        }}
        .article-title {{
            font-weight: bold;
            color: #007acc;
            margin-bottom: 8px;
        }}
        .article-meta {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        .category-header {{
            background: #007acc;
            color: white;
            padding: 10px;
            margin: 20px 0 10px 0;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 DEBUG: Bob's Brief</h1>
        <p><strong>Debug Mode:</strong> {date_formatted}</p>
        
        <div class="debug-info">
            <h3>🔍 Debug Information</h3>
            <p><strong>Total articles loaded from JSON:</strong> {len(news_data)}</p>
            <p><strong>Unique articles after deduplication:</strong> {len(unique_articles)}</p>
            <p><strong>Categories found:</strong> {len(categories)}</p>
            <p><strong>Generated at:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
"""
    
    if categories:
        for category, articles in categories.items():
            html_content += f"""
        <div class="category-header">
            📂 {category} ({len(articles)} articles)
        </div>
"""
            for i, article in enumerate(articles[:6]):  # Show max 6 per category
                title = article.get('Title', 'No Title')
                source = article.get('Source', 'Unknown Source')
                published = article.get('Published', 'Unknown Date')
                link = article.get('Link', '#')
                
                html_content += f"""
        <div class="article">
            <div class="article-title">
                <a href="{link}" target="_blank">{title}</a>
            </div>
            <div class="article-meta">
                Source: {source} | Published: {published}
            </div>
        </div>
"""
    else:
        html_content += """
        <div class="debug-info">
            <h3>❌ No Categories Found</h3>
            <p>The JSON file was loaded but no categories were processed.</p>
        </div>
"""
    
    html_content += """
    </div>
    
    <script>
        console.log('DEBUG: HTML page loaded');
        console.log('DEBUG: Articles found:', """ + str(len(unique_articles)) + """);
        console.log('DEBUG: Categories:', """ + str(list(categories.keys())) + """);
    </script>
</body>
</html>
"""
    
    # Save HTML file
    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("🔍 DEBUG: Enhanced visual newsletter generated successfully!")
    print(f"🔍 DEBUG: Generated briefing with {len(unique_articles)} unique articles")
    print(f"🔍 DEBUG: Categories: {list(categories.keys())}")
    
    return len(unique_articles)

def remove_duplicate_articles(articles):
    """Remove duplicate articles based on title similarity"""
    if not articles:
        return []
    
    unique_articles = []
    seen_titles = []
    
    for article in articles:
        title = article.get('Title', '').lower().strip()
        if not title:
            continue
            
        title_words = set(title.split())
        
        is_duplicate = False
        for seen_title in seen_titles:
            seen_words = set(seen_title.split())
            if len(title_words) > 0 and len(seen_words) > 0:
                similarity = len(title_words.intersection(seen_words)) / max(len(title_words), len(seen_words))
                if similarity > 0.7:
                    is_duplicate = True
                    break
        
        if not is_duplicate:
            seen_titles.append(title)
            unique_articles.append(article)
    
    return unique_articles

if __name__ == "__main__":
    generate_html()
