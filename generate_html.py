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
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .header {{
            background: linear-gradient(135deg, #1a73e8 0%, #4285f4 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 4s ease-in-out infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); opacity: 0.5; }}
            50% {{ transform: scale(1.1); opacity: 0.8; }}
        }}
        
        .header-content {{
            position: relative;
            z-index: 2;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            font-weight: 700;
        }}
        
        .search-info {{
            font-size: 1.2em;
            opacity: 0.95;
            margin-top: 15px;
        }}
        
        .search-query {{
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 25px;
            font-family: 'Courier New', monospace;
            font-weight: 600;
            margin: 0 8px;
            display: inline-block;
        }}
        
        .main-content {{
            padding: 40px;
        }}
        
        .search-controls {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
            border-left: 5px solid #1a73e8;
        }}
        
        .search-controls h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .current-search {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }}
        
        .current-search strong {{
            color: #1a73e8;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }}
        
        .stat {{
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .stat:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #1a73e8;
            margin-bottom: 5px;
            background: linear-gradient(45deg, #1a73e8, #4285f4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .stat-label {{
            color: #6c757d;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.9em;
        }}
        
        .news-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
        }}
        
        .news-item {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            border-left: 4px solid #1a73e8;
            position: relative;
            overflow: hidden;
        }}
        
        .news-item::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, #1a73e8, #4285f4, #34a853, #fbbc04);
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }}
        
        .news-item:hover {{
            transform: translateY(-8px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        }}
        
        .news-item:hover::before {{
            transform: scaleX(1);
        }}
        
        .news-title {{
            margin: 0 0 20px 0;
            font-size: 1.3em;
            line-height: 1.4;
            font-weight: 600;
        }}
        
        .news-title a {{
            color: #2c3e50;
            text-decoration: none;
            transition: color 0.3s ease;
        }}
        
        .news-title a:hover {{
            color: #1a73e8;
        }}
        
        .news-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid #e9ecef;
        }}
        
        .news-source {{
            background: linear-gradient(135deg, #1a73e8, #4285f4);
            color: white;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .news-time {{
            color: #6c757d;
            font-size: 0.9em;
            font-weight: 500;
        }}
        
        .no-results {{
            text-align: center;
            background: linear-gradient(135deg, #fff5f5 0%, #fed7d7 100%);
            padding: 50px;
            border-radius: 15px;
            border: 2px dashed #fc8181;
        }}
        
        .no-results h3 {{
            color: #e53e3e;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        
        .no-results ul {{
            text-align: left;
            display: inline-block;
            color: #744c4c;
            margin: 20px 0;
        }}
        
        .footer {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            text-align: center;
            padding: 40px;
            margin-top: 50px;
        }}
        
        .footer-content {{
            max-width: 800px;
            margin: 0 auto;
        }}
        
        .refresh-btn {{
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            font-size: 1.1em;
            font-weight: 600;
            margin-top: 25px;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(40, 167, 69, 0.3);
        }}
        
        .refresh-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(40, 167, 69, 0.4);
            background: linear-gradient(135deg, #218838, #1cc88a);
        }}
        
        .debug-info {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            font-size: 0.9em;
            color: #6c757d;
            border-left: 4px solid #17a2b8;
        }}
        
        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: blink 2s infinite;
        }}
        
        .status-success {{
            background: #28a745;
        }}
        
        .status-warning {{
            background: #ffc107;
        }}
        
        .status-error {{
            background: #dc3545;
        }}
        
        @keyframes blink {{
            0%, 50% {{ opacity: 1; }}
            51%, 100% {{ opacity: 0.3; }}
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            
            .header {{
                padding: 30px 20px;
            }}
            
            .header h1 {{
                font-size: 2em;
                flex-direction: column;
                gap: 10px;
            }}
            
            .main-content {{
                padding: 30px 20px;
            }}
            
            .news-container {{
                grid-template-columns: 1fr;
            }}
            
            .stats {{
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }}
            
            .news-meta {{
                flex-direction: column;
                align-items: flex-start;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <h1>
                    🔍 Google News Search
                </h1>
                <div class="search-info">
                    Searching for: <span class="search-query">{search_query}</span>
                    <br>Timeframe: {timeframe} • Updated automatically every 6 hours
                </div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="search-controls">
                <h3>🎯 Current Search Parameters</h3>
                <div class="current-search">
                    <strong>Query:</strong> {search_query}<br>
                    <strong>Time Range:</strong> {timeframe}<br>
                    <strong>Last Search:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                    <strong>Search URL:</strong> <code>https://news.google.com/search?q=china AND russian AND cyber when:24h</code>
                </div>
            </div>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">{len(news_data)}</div>
                    <div class="stat-label">Articles Found</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{datetime.now().strftime('%H:%M')}</div>
                    <div class="stat-label">Last Updated</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{"✓" if news_data else "✗"}</div>
                    <div class="stat-label">Status</div>
                </div>
            </div>
            
            <div class="news-container">
"""
    
    # Add news items or no results message
    if news_data:
        status_class = "status-success"
        for item in news_data:
            # Format published time
            pub_time = item.get('Published', 'Unknown')
            if pub_time and pub_time != 'Unknown' and pub_time != 'Recent':
                try:
                    # Try to format the time nicely
                    if 'T' in pub_time:
                        dt = datetime.fromisoformat(pub_time.replace('Z', '+00:00'))
                        pub_time = dt.strftime('%B %d, %Y %I:%M %p')
                except:
                    pass
            elif pub_time == 'Recent':
                pub_time = 'Recently published'
            
            html_content += f"""
            <div class="news-item">
                <h3 class="news-title">
                    <a href="{item['Link']}" target="_blank" rel="noopener noreferrer">{item['Title']}</a>
                </h3>
                <div class="news-meta">
                    <span class="news-source">{item['Source']}</span>
                    <span class="news-time">📅 {pub_time}</span>
                </div>
            </div>
            """
    else:
        status_class = "status-error"
        html_content += """
            <div class="no-results">
                <h3>🚫 No articles found</h3>
                <p>The search didn't return any valid news articles. This could be because:</p>
                <ul>
                    <li>The search terms are too specific for the last 24 hours</li>
                    <li>Google News structure has changed</li>
                    <li>The scraper is being blocked or rate-limited</li>
                    <li>Navigation items are being detected instead of articles</li>
                </ul>
                <div class="debug-info">
                    <strong>🔧 Debug Info:</strong> Check the GitHub Actions logs for detailed scraping information, 
                    including what elements were found and why they were filtered out.
                </div>
            </div>
        """
    
    html_content += f"""
            </div>
        </div>
        
        <div class="footer">
            <div class="footer-content">
                <p><span class="{status_class} status-indicator"></span><strong>🔍 Search Results from Google News</strong></p>
                <p>Query: "<strong>{search_query}</strong>" | Timeframe: <strong>{timeframe}</strong></p>
                <p>Last updated: <strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</strong> UTC</p>
                
                <button class="refresh-btn" onclick="location.reload()">
                    🔄 Refresh Results
                </button>
                
                <div class="debug-info">
                    <strong>🔧 Technical Details:</strong><br>
                    • Search URL: <code>https://news.google.com/search?q=china AND russian AND cyber when:24h</code><br>
                    • Scraping Strategy: Multi-level article detection with navigation filtering<br>
                    • Update Frequency: Every 6 hours via GitHub Actions<br>
                    • Articles Found: {len(news_data)} valid articles after filtering
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 10 minutes to show any new results
        setTimeout(function() {{
            location.reload();
        }}, 600000);
        
        // Add click tracking and smooth scrolling
        document.querySelectorAll('.news-title a').forEach(link => {{
            link.addEventListener('click', function() {{
                console.log('Article clicked:', this.textContent);
                
                // Add a visual click effect
                this.style.transform = 'scale(0.98)';
                setTimeout(() => {{
                    this.style.transform = 'scale(1)';
                }}, 150);
            }});
        }});
        
        // Add hover effects for stats
        document.querySelectorAll('.stat').forEach(stat => {{
            stat.addEventListener('mouseenter', function() {{
                this.style.transform = 'translateY(-5px) scale(1.02)';
            }});
            
            stat.addEventListener('mouseleave', function() {{
                this.style.transform = 'translateY(0) scale(1)';
            }});
        }});
        
        // Display current time
        function updateTime() {{
            const now = new Date();
            const timeString = now.toLocaleTimeString('en-US', {{
                hour12: false,
                hour: '2-digit',
                minute: '2-digit'
            }});
            
            // Update the time display if it exists
            const timeElements = document.querySelectorAll('.stat-number');
            if (timeElements.length >= 2) {{
                timeElements[1].textContent = timeString;
            }}
        }}
        
        // Update time every minute
        setInterval(updateTime, 60000);
        
        // Add loading animation for refresh button
        document.querySelector('.refresh-btn').addEventListener('click', function() {{
            this.innerHTML = '⏳ Refreshing...';
            this.disabled = true;
        }});
        
        // Console info for debugging
        console.log('Google News Search Results Page Loaded');
        console.log('Articles found:', {len(news_data)});
        console.log('Last updated:', '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}');
    </script>
</body>
</html>
"""
    
    # Save HTML file
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("HTML page generated successfully for search results!")
    print(f"Generated page with {len(news_data)} articles")
    if news_data:
        print("Sample articles:")
        for i, article in enumerate(news_data[:3]):
            print(f"  {i+1}. {article['Title'][:60]}...")

if __name__ == "__main__":
    generate_html()
