import json
import os
from datetime import datetime

def generate_html():
    """Generate HTML page in newsletter/Substack style"""
    
    # Load the latest news data
    try:
        with open("data/latest_news.json", "r", encoding="utf-8") as f:
            news_data = json.load(f)
    except FileNotFoundError:
        news_data = []
    
    # Group articles by category
    categories = {}
    for article in news_data:
        category = article.get('Category', 'General Cyber')
        if category not in categories:
            categories[category] = []
        categories[category].append(article)
    
    # Get current date for newsletter header
    current_date = datetime.now()
    date_formatted = current_date.strftime("%B %d, %Y")
    day_of_year = current_date.timetuple().tm_yday
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyber Intelligence Brief - {date_formatted}</title>
    <style>
        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            line-height: 1.6;
            color: #1a1a1a;
            background-color: #ffffff;
            margin: 0;
            padding: 0;
        }}
        
        .container {{
            max-width: 680px;
            margin: 0 auto;
            padding: 40px 20px;
            background-color: #ffffff;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 50px;
            padding-bottom: 30px;
            border-bottom: 1px solid #e6e6e6;
        }}
        
        .title {{
            font-size: 2.5em;
            font-weight: bold;
            color: #1a1a1a;
            margin-bottom: 10px;
            letter-spacing: -0.5px;
        }}
        
        .subtitle {{
            font-size: 1.2em;
            color: #666666;
            margin-bottom: 15px;
            font-style: italic;
        }}
        
        .date-info {{
            font-size: 0.95em;
            color: #888888;
            margin-bottom: 5px;
        }}
        
        .issue-number {{
            font-size: 0.9em;
            color: #888888;
            font-weight: 500;
        }}
        
        .intro {{
            font-size: 1.1em;
            line-height: 1.7;
            color: #333333;
            margin-bottom: 40px;
            padding: 25px;
            background-color: #f8f9fa;
            border-left: 4px solid #007acc;
            border-radius: 4px;
        }}
        
        .section {{
            margin-bottom: 45px;
        }}
        
        .section-header {{
            font-size: 1.4em;
            font-weight: bold;
            color: #1a1a1a;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #007acc;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .article {{
            margin-bottom: 30px;
            padding-bottom: 25px;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .article:last-child {{
            border-bottom: none;
            margin-bottom: 0;
        }}
        
        .article-title {{
            font-size: 1.2em;
            font-weight: bold;
            line-height: 1.4;
            margin-bottom: 8px;
        }}
        
        .article-title a {{
            color: #1a1a1a;
            text-decoration: none;
            transition: color 0.2s ease;
        }}
        
        .article-title a:hover {{
            color: #007acc;
        }}
        
        .article-meta {{
            font-size: 0.9em;
            color: #666666;
            margin-bottom: 10px;
        }}
        
        .source {{
            font-weight: 600;
            color: #007acc;
        }}
        
        .time {{
            margin-left: 10px;
        }}
        
        .article-summary {{
            font-size: 1em;
            line-height: 1.6;
            color: #444444;
            margin-top: 8px;
        }}
        
        .stats-box {{
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .stat {{
            display: inline-block;
            margin: 0 15px;
        }}
        
        .stat-number {{
            font-size: 1.8em;
            font-weight: bold;
            color: #007acc;
            display: block;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            color: #666666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .footer {{
            margin-top: 50px;
            padding-top: 30px;
            border-top: 1px solid #e6e6e6;
            text-align: center;
            color: #888888;
            font-size: 0.9em;
        }}
        
        .footer-links {{
            margin-top: 15px;
        }}
        
        .footer-links a {{
            color: #007acc;
            text-decoration: none;
            margin: 0 10px;
        }}
        
        .footer-links a:hover {{
            text-decoration: underline;
        }}
        
        .highlight-box {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 6px;
            padding: 20px;
            margin: 25px 0;
        }}
        
        .highlight-title {{
            font-weight: bold;
            color: #856404;
            margin-bottom: 10px;
        }}
        
        .no-articles {{
            text-align: center;
            padding: 40px;
            color: #666666;
            font-style: italic;
        }}
        
        @media (max-width: 600px) {{
            .container {{
                padding: 20px 15px;
            }}
            
            .title {{
                font-size: 2em;
            }}
            
            .stats-box {{
                padding: 15px;
            }}
            
            .stat {{
                display: block;
                margin: 10px 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">Cyber Intelligence Brief</h1>
            <p class="subtitle">Daily cybersecurity intelligence from global sources</p>
            <p class="date-info">{date_formatted}</p>
            <p class="issue-number">Issue #{day_of_year}</p>
        </div>
        
        <div class="intro">
            <strong>Welcome to today's cyber intelligence briefing.</strong> This automated digest aggregates the latest cybersecurity developments, threat intelligence, and geopolitical cyber activities from the past 24 hours. Our system monitors multiple categories including nation-state activities, cyber attacks, and security industry developments.
        </div>
        
        <div class="stats-box">
            <div class="stat">
                <span class="stat-number">{len(news_data)}</span>
                <span class="stat-label">Articles Today</span>
            </div>
            <div class="stat">
                <span class="stat-number">{len(categories)}</span>
                <span class="stat-label">Categories</span>
            </div>
            <div class="stat">
                <span class="stat-number">{current_date.strftime('%H:%M')}</span>
                <span class="stat-label">Last Updated</span>
            </div>
        </div>
"""
    
    # Add sections for each category
    if categories:
        # Define category order and descriptions
        category_info = {
            'China Cyber': '🇨🇳 China-related cyber operations and digital policy developments',
            'Russian Cyber': '🇷🇺 Russian cyber activities and state-sponsored operations', 
            'Iran Cyber': '🇮🇷 Iranian cyber capabilities and regional digital warfare',
            'General Cyber': '🌐 Broad cybersecurity developments and industry news',
            'Cybersecurity': '🔒 Enterprise security, defense technologies, and best practices',
            'Cyber Attacks': '⚠️ Recent incidents, breaches, and threat actor activities'
        }
        
        for category, description in category_info.items():
            if category in categories:
                articles = categories[category]
                html_content += f"""
        <div class="section">
            <h2 class="section-header">{category}</h2>
            <p style="color: #666666; margin-bottom: 25px; font-style: italic;">{description}</p>
"""
                
                for article in articles:
                    # Format published time
                    pub_time = article.get('Published', 'Unknown')
                    if pub_time and pub_time != 'Unknown' and pub_time != 'Recent':
                        try:
                            if 'T' in pub_time:
                                dt = datetime.fromisoformat(pub_time.replace('Z', '+00:00'))
                                pub_time = dt.strftime('%I:%M %p')
                        except:
                            pass
                    elif pub_time == 'Recent':
                        pub_time = 'Recently published'
                    
                    # Create article summary (first 150 chars of title as description)
                    title = article['Title']
                    summary = ""
                    if len(title) > 80:
                        # Create a brief summary from the title
                        words = title.split()
                        if len(words) > 12:
                            summary = " ".join(words[8:]) + "..."
                    
                    html_content += f"""
            <div class="article">
                <h3 class="article-title">
                    <a href="{article['Link']}" target="_blank" rel="noopener noreferrer">{title}</a>
                </h3>
                <div class="article-meta">
                    <span class="source">{article['Source']}</span>
                    <span class="time">• {pub_time}</span>
                </div>
                {f'<div class="article-summary">{summary}</div>' if summary else ''}
            </div>
"""
                
                html_content += """        </div>"""
        
        # Add highlight box for key developments
        if len(news_data) > 0:
            html_content += f"""
        <div class="highlight-box">
            <div class="highlight-title">📊 Today's Intelligence Summary</div>
            <p>Our monitoring systems identified <strong>{len(news_data)} relevant developments</strong> across <strong>{len(categories)} categories</strong> in the past 24 hours. Key focus areas include nation-state cyber activities, security incidents, and policy developments affecting the global threat landscape.</p>
        </div>
"""
    else:
        html_content += """
        <div class="no-articles">
            <h3>No Intelligence Gathered Today</h3>
            <p>Our monitoring systems did not identify any relevant cyber intelligence in the past 24 hours matching our collection criteria. This could indicate quiet threat actor activity or collection system maintenance.</p>
        </div>
"""
    
    html_content += f"""
        <div class="footer">
            <p><strong>Cyber Intelligence Brief</strong> | Automated Intelligence Collection</p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
            <div class="footer-links">
                <a href="#" onclick="location.reload()">Refresh Report</a>
                <a href="https://github.com/arandomguyhere/Google-News-Scraper" target="_blank">View Source</a>
            </div>
            <p style="margin-top: 20px; font-size: 0.8em; color: #aaa;">
                This briefing is generated automatically from public news sources. 
                Information is for situational awareness purposes only.
            </p>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 minutes
        setTimeout(function() {{
            location.reload();
        }}, 1800000);
        
        // Add click tracking
        document.querySelectorAll('.article-title a').forEach(link => {{
            link.addEventListener('click', function() {{
                console.log('Article clicked:', this.textContent);
            }});
        }});
        
        console.log('Cyber Intelligence Brief loaded');
        console.log('Articles:', {len(news_data)});
        console.log('Categories:', {len(categories)});
    </script>
</body>
</html>
"""
    
    # Save HTML file
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("Newsletter-style HTML page generated successfully!")
    print(f"Generated briefing with {len(news_data)} articles across {len(categories)} categories")

if __name__ == "__main__":
    generate_html()
