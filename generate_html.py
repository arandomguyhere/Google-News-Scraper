import json
import os
from datetime import datetime

def generate_html():
    """Generate HTML page from scraped news data"""
    
    # Load the latest news data
    try:
        with open("data/latest_news.json", "r", encoding="utf-8") as f:
            news_data = json.load(f)
    except FileNotFoundError:
        news_data = []
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google News Scraper - Latest Headlines</title>
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
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
            color: #667eea;
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
            transition: transform 0.2s;
        }}
        
        .news-item:hover {{
            transform: translateY(-5px);
        }}
        
        .news-title {{
            margin: 0 0 10px 0;
            font-size: 1.2em;
            line-height: 1.4;
        }}
        
        .news-title a {{
            color: #333;
            text-decoration: none;
        }}
        
        .news-title a:hover {{
            color: #667eea;
        }}
        
        .news-meta {{
            color: #666;
            font-size: 0.9em;
            margin-top: 10px;
        }}
        
        .news-source {{
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            margin-right: 10px;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: #666;
        }}
        
        .refresh-btn {{
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin-top: 20px;
        }}
        
        .refresh-btn:hover {{
            background: #5a67d8;
        }}
        
        @media (max-width: 768px) {{
            .news-container {{
                grid-template-columns: 1fr;
            }}
            
            .stats {{
                flex-direction: column;
                gap: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📰 Google News Scraper</h1>
        <p>Latest headlines updated automatically every 6 hours</p>
    </div>
    
    <div class="stats">
        <div class="stat">
            <div class="stat-number">{len(news_data)}</div>
            <div>Articles</div>
        </div>
        <div class="stat">
            <div class="stat-number">{datetime.now().strftime('%H:%M')}</div>
            <div>Last Updated</div>
        </div>
    </div>
    
    <div class="news-container">
"""
    
    # Add news items
    for item in news_data:
        html_content += f"""
        <div class="news-item">
            <h3 class="news-title">
                <a href="{item['Link']}" target="_blank">{item['Title']}</a>
            </h3>
            <div class="news-meta">
                <span class="news-source">{item['Source']}</span>
                <span>Published: {item['Published']}</span>
            </div>
        </div>
        """
    
    if not news_data:
        html_content += """
        <div class="news-item">
            <h3 class="news-title">No news available</h3>
            <p>The scraper hasn't collected any news yet or encountered an error.</p>
        </div>
        """
    
    html_content += f"""
    </div>
    
    <div class="footer">
        <p>Data scraped from Google News | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <button class="refresh-btn" onclick="location.reload()">Refresh Page</button>
    </div>
    
    <script>
        // Auto-refresh every 5 minutes
        setTimeout(function() {{
            location.reload();
        }}, 300000);
    </script>
</body>
</html>
"""
    
    # Save HTML file
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("HTML page generated successfully!")

if __name__ == "__main__":
    generate_html()
