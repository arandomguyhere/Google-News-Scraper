import json
import os
from datetime import datetime

def generate_html():
    """Generate HTML page from scraped news search results"""
    
    # Load the latest news data
    try:
        with open("data/latest_news.json", "r", encoding="utf-8") as f:
            news_data = json.load(f)
    except FileNotFoundError:
        news_data = []
    
    # Search query info
    search_query = "china AND russian AND cyber"
    timeframe = "Last 24 hours"
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google News Search: {search_query}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        
        .header {{
            text-align: center;
            background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.2em;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}
        
        .search-info {{
            margin: 15px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .search-query {{
            background: rgba(255,255,255,0.2);
            padding: 5px 10px;
            border-radius: 5px;
            font-family: monospace;
            margin: 0 5px;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .stat {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #1a73e8;
        }}
        
        .news-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }}
        
        .news-item {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            border-left: 4px solid #1a73e8;
        }}
        
        .news-item:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }}
        
        .news-title {{
            margin: 0 0 15px 0;
            font-size: 1.2em;
            line-height: 1.4;
        }}
        
        .news-title a {{
            color: #1a73e8;
            text-decoration: none;
            font-weight: 600;
        }}
        
        .news-title a:hover {{
            text-decoration: underline;
        }}
        
        .news-meta {{
            color: #666;
            font-size: 0.9em;
            margin-top: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .news-source {{
            background: #1a73e8;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 500;
        }}
        
        .news-time {{
            color: #888;
            font-size: 0.85em;
        }}
        
        .no-results {{
            text-align: center;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .no-results h3 {{
            color: #666;
            margin-bottom: 10px;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: #666;
        }}
        
        .refresh-btn {{
            background: #1a73e8;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1em;
            margin-top: 20px;
            transition: background-color 0.2s;
        }}
        
        .refresh-btn:hover {{
            background: #1557b0;
        }}
        
        .search-controls {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .search-controls h3 {{
            margin: 0 0 15px 0;
            color: #333;
        }}
        
        .current-search {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #1a73e8;
        }}
        
        @media (max-width: 768px) {{
            .news-container {{
                grid-template-columns: 1fr;
            }}
            
            .stats {{
                flex-direction: column;
                gap: 15px;
            }}
            
            .header h1 {{
                font-size: 1.8em;
                flex-direction: column;
            }}
            
            .news-meta {{
                flex-direction: column;
                align-items: flex-start;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>
            🔍 Google News Search
        </h1>
        <div class="search-info">
            Searching for: <span class="search-query">{search_query}</span>
            <br>Timeframe: {timeframe} • Updated automatically every 6 hours
        </div>
    </div>
    
    <div class="search-controls">
        <h3>Current Search Parameters</h3>
        <div class="current-search">
            <strong>Query:</strong> {search_query}<br>
            <strong>Time Range:</strong> {timeframe}<br>
            <strong>Last Search:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-number">{len(news_data)}</div>
            <div>Articles Found</div>
        </div>
        <div class="stat">
            <div class="stat-number">{datetime.now().strftime('%H:%M')}</div>
            <div>Last Updated</div>
        </div>
    </div>
    
    <div class="news-container">
"""
    
    # Add news items
    if news_data:
        for item in news_data:
            # Format published time
            pub_time = item.get('Published', 'Unknown')
            if pub_time and pub_time != 'Unknown':
                try:
                    # Try to format the time nicely
                    if 'T' in pub_time:
                        dt = datetime.fromisoformat(pub_time.replace('Z', '+00:00'))
                        pub_time = dt.strftime('%B %d, %Y %I:%M %p')
                except:
                    pass
            
            html_content += f"""
        <div class="news-item">
            <h3 class="news-title">
                <a href="{item['Link']}" target="_blank">{item['Title']}</a>
            </h3>
            <div class="news-meta">
                <span class="news-source">{item['Source']}</span>
                <span class="news-time">Published: {pub_time}</span>
            </div>
        </div>
        """
    else:
        html_content += """
        <div class="no-results">
            <h3>No articles found</h3>
            <p>The search didn't return any results. This could be because:</p>
            <ul style="text-align: left; display: inline-block;">
                <li>The search terms are too specific</li>
                <li>No recent articles match the criteria</li>
                <li>Google News structure has changed</li>
                <li>Rate limiting or blocking occurred</li>
            </ul>
            <p>The scraper will try again in the next scheduled run.</p>
        </div>
        """
    
    html_content += f"""
    </div>
    
    <div class="footer">
        <p>🔍 <strong>Search Results from Google News</strong></p>
        <p>Query: "{search_query}" | Timeframe: {timeframe}</p>
        <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
        <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Results</button>
        <br><br>
        <small>This page automatically updates every 6 hours with fresh search results</small>
    </div>
    
    <script>
        // Auto-refresh every 10 minutes to show any new results
        setTimeout(function() {{
            location.reload();
        }}, 600000);
        
        // Add click tracking
        document.querySelectorAll('.news-title a').forEach(link => {{
            link.addEventListener('click', function() {{
                console.log('Clicked article:', this.textContent);
            }});
        }});
    </script>
</body>
</html>
"""
    
    # Save HTML file
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("HTML page generated successfully for search results!")

if __name__ == "__main__":
    generate_html()
