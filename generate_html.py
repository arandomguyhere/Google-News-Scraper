import json
import os
from datetime import datetime

def generate_html():
    """Generate enhanced visual newsletter with images and duplicate removal"""
    
    # Load the latest news data
    try:
        with open("data/latest_news.json", "r", encoding="utf-8") as f:
            news_data = json.load(f)
    except FileNotFoundError:
        news_data = []
    
    # Remove duplicates based on title similarity
    unique_articles = remove_duplicate_articles(news_data)
    
    # Group articles by category
    categories = {}
    for article in unique_articles:
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
            max-width: 800px;
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
        
        .section {{
            margin-bottom: 50px;
        }}
        
        .section-header {{
            font-size: 1.4em;
            font-weight: bold;
            color: #1a1a1a;
            margin-bottom: 25px;
            padding-bottom: 10px;
            border-bottom: 2px solid #007acc;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .section-description {{
            color: #666666;
            margin-bottom: 30px;
            font-style: italic;
            font-size: 1em;
        }}
        
        .articles-grid {{
            display: grid;
            gap: 25px;
        }}
        
        .article {{
            display: flex;
            background: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            overflow: hidden;
            transition: box-shadow 0.2s ease, transform 0.2s ease;
            text-decoration: none;
            color: inherit;
        }}
        
        .article:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        
        .article-image {{
            width: 200px;
            height: 140px;
            flex-shrink: 0;
            background-color: #f8f9fa;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }}
        
        .article-image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        
        .article-image-placeholder {{
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #007acc, #0056b3);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            color: white;
        }}
        
        .article-content {{
            flex: 1;
            padding: 20px;
            display: flex;
            flex-direction: column;
        }}
        
        .article-title {{
            font-size: 1.2em;
            font-weight: bold;
            line-height: 1.4;
            margin-bottom: 10px;
            color: #1a1a1a;
            text-decoration: none;
        }}
        
        .article-meta {{
            font-size: 0.9em;
            color: #666666;
            margin-bottom: 12px;
        }}
        
        .source {{
            font-weight: 600;
            color: #007acc;
        }}
        
        .time {{
            margin-left: 8px;
        }}
        
        .article-summary {{
            font-size: 0.95em;
            line-height: 1.5;
            color: #444444;
            flex-grow: 1;
        }}
        
        .category-stats {{
            background-color: #f1f8ff;
            border: 1px solid #c8e1ff;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 25px;
            font-size: 0.9em;
            color: #0366d6;
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
        
        .no-articles {{
            text-align: center;
            padding: 40px;
            color: #666666;
            font-style: italic;
        }}
        
        @media (max-width: 700px) {{
            .container {{
                padding: 20px 15px;
            }}
            
            .title {{
                font-size: 2em;
            }}
            
            .article {{
                flex-direction: column;
            }}
            
            .article-image {{
                width: 100%;
                height: 200px;
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
                <span class="stat-number">{len(unique_articles)}</span>
                <span class="stat-label">Unique Articles</span>
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
        # Define category order and descriptions with icons - expanded from Bob's analysis
        category_info = {
            # Core Nation-State Actors
            'China Cyber': ('🇨🇳', 'China-related cyber operations and digital policy developments'),
            'Russian Cyber': ('🇷🇺', 'Russian cyber activities and state-sponsored operations'), 
            'Iran Cyber': ('🇮🇷', 'Iranian cyber capabilities and regional digital warfare'),
            
            # Threat Intelligence
            'APT Groups': ('🎭', 'Advanced Persistent Threat groups and sophisticated actors'),
            'Advanced Threats': ('⚡', 'Elite threat actors and nation-state campaigns'),
            'Ransomware': ('🔒', 'Ransomware attacks and criminal groups'),
            
            # Critical Infrastructure
            'Critical Infrastructure': ('🏭', 'Power grids, water systems, and essential services'),
            'Energy Security': ('⚡', 'Power grid and energy infrastructure threats'),
            'Supply Chain': ('🔗', 'Supply chain attacks and vendor compromises'),
            
            # Vulnerabilities & Exploits
            'Zero Days': ('🚨', 'Zero-day exploits and undisclosed vulnerabilities'),
            'Vulnerabilities': ('🔓', 'CVEs and security flaws in software systems'),
            'VPN Security': ('🔒', 'VPN vulnerabilities and enterprise access threats'),
            
            # Emerging Technologies
            'AI Security': ('🤖', 'Artificial intelligence security and AI-powered attacks'),
            'Quantum Threats': ('⚛️', 'Quantum computing impact on cybersecurity'),
            'Blockchain Security': ('⛓️', 'Cryptocurrency and blockchain vulnerabilities'),
            
            # Geopolitical Cyber
            'Taiwan Security': ('🇹🇼', 'Taiwan-focused cyber threats and geopolitical tensions'),
            'Ukraine Conflict': ('🇺🇦', 'Ukraine-Russia cyber warfare and digital conflict'),
            'Middle East Cyber': ('🇮🇱', 'Middle East cyber operations and regional threats'),
            
            # Attack Methods
            'Phishing': ('🎣', 'Email phishing and social engineering campaigns'),
            'Malware': ('🦠', 'Malicious software and payload analysis'),
            'Social Engineering': ('🎭', 'Human-factor attacks and manipulation tactics'),
            
            # Industry Sectors
            'Healthcare Security': ('🏥', 'Medical device security and healthcare data breaches'),
            'Financial Security': ('💳', 'Banking, fintech, and financial system threats'),
            'Maritime Security': ('⚓', 'Port systems and maritime infrastructure cybersecurity'),
            
            # Technology & Infrastructure
            'Tech Companies': ('📱', 'Technology vendor security and corporate espionage'),
            '5G Networks': ('📡', '5G infrastructure security and telecommunications threats'),
            'IoT Security': ('📟', 'Internet of Things and connected device vulnerabilities'),
            
            # General Categories
            'Cybersecurity': ('🛡️', 'Enterprise security, defense technologies, and best practices'),
            'Cyber Attacks': ('⚠️', 'Recent incidents, breaches, and threat actor activities')
        }
        
        for category, (icon, description) in category_info.items():
            if category in categories:
                articles = categories[category]
                html_content += f"""
        <div class="section">
            <h2 class="section-header">{icon} {category}</h2>
            <p class="section-description">{description}</p>
            <div class="category-stats">
                <strong>{len(articles)}</strong> articles found in this category
            </div>
            <div class="articles-grid">
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
                    
                    # Create article summary from title
                    title = article['Title']
                    summary = create_summary(title)
                    
                    # Get placeholder icon for category
                    placeholder_icon = get_category_icon(category)
                    
                    # Check if article has an image and log it
                    article_image = article.get('img', '')
                    image_html = ""
                    
                    print(f"  Processing article: {title[:40]}...")
                    print(f"    Image URL: {article_image if article_image else 'None'}")
                    
                    if article_image and article_image.startswith('http') and not article_image.startswith('data:'):
                        # Use real image from Google News
                        image_html = f'<img src="{article_image}" alt="Article image" loading="lazy" onerror="this.parentElement.innerHTML=\'<div class=&quot;article-image-placeholder&quot;>{placeholder_icon}</div>\'">'
                        print(f"    Using real image: {article_image[:60]}...")
                    else:
                        # Use placeholder
                        image_html = f'<div class="article-image-placeholder">{placeholder_icon}</div>'
                        print(f"    Using placeholder icon: {placeholder_icon}")
                    
                    html_content += f"""
                <a href="{article['Link']}" target="_blank" rel="noopener noreferrer" class="article">
                    <div class="article-image">
                        {image_html}
                    </div>
                    <div class="article-content">
                        <h3 class="article-title">{title}</h3>
                        <div class="article-meta">
                            <span class="source">{article['Source']}</span>
                            <span class="time">• {pub_time}</span>
                        </div>
                        {f'<div class="article-summary">{summary}</div>' if summary else ''}
                    </div>
                </a>
"""
                
                html_content += """            </div>
        </div>"""
        
        # Add intelligence summary
        duplicate_count = len(news_data) - len(unique_articles)
        html_content += f"""
        <div class="highlight-box">
            <div class="highlight-title">📊 Today's Intelligence Summary</div>
            <p>Our monitoring systems identified <strong>{len(news_data)} total developments</strong> across <strong>{len(categories)} categories</strong> in the past 24 hours. After deduplication, <strong>{len(unique_articles)} unique articles</strong> remain for analysis. {f'<strong>{duplicate_count} duplicate articles</strong> were filtered out to ensure content quality.' if duplicate_count > 0 else ''}</p>
        </div>
"""
    else:
        html_content += """
        <div class="no-articles">
            <h3>No Intelligence Gathered Today</h3>
            <p>Our monitoring systems did not identify any relevant cyber intelligence in the past 24 hours matching our collection criteria.</p>
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
        
        // Handle image loading errors
        document.querySelectorAll('.article-image img').forEach(img => {{
            img.addEventListener('error', function() {{
                this.parentElement.innerHTML = '<div class="article-image-placeholder">📰</div>';
            }});
        }});
        
        console.log('Enhanced Cyber Intelligence Brief loaded');
        console.log('Total articles collected:', {len(news_data)});
        console.log('Unique articles after deduplication:', {len(unique_articles)});
        console.log('Categories:', {len(categories)});
    </script>
</body>
</html>
"""
    
    # Save HTML file
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("Enhanced visual newsletter generated successfully!")
    print(f"Generated briefing with {len(unique_articles)} unique articles (filtered {len(news_data) - len(unique_articles)} duplicates)")
    print(f"Categories: {list(categories.keys())}")
    
    # Debug: Count articles with images
    articles_with_images = sum(1 for article in unique_articles if article.get('img'))
    print(f"Articles with images: {articles_with_images}/{len(unique_articles)}")
    
    if articles_with_images > 0:
        print("Sample image URLs:")
        for article in unique_articles[:3]:
            if article.get('img'):
                print(f"  - {article['Title'][:40]}... -> {article['img'][:60]}...")
    else:
        print("No images found - will use placeholders")

def remove_duplicate_articles(articles):
    """Remove duplicate articles based on title similarity"""
    if not articles:
        return []
    
    unique_articles = []
    seen_titles = []
    
    for article in articles:
        title = article['Title'].lower().strip()
        title_words = set(title.split())
        
        # Check if this title is too similar to existing ones
        is_duplicate = False
        for seen_title in seen_titles:
            seen_words = set(seen_title.split())
            if len(title_words) > 0 and len(seen_words) > 0:
                # Calculate word overlap
                common_words = title_words.intersection(seen_words)
                similarity = len(common_words) / max(len(title_words), len(seen_words))
                
                # If more than 70% similarity, consider it a duplicate
                if similarity > 0.7:
                    is_duplicate = True
                    print(f"Filtering duplicate: {article['Title'][:60]}...")
                    break
        
        if not is_duplicate:
            seen_titles.append(title)
            unique_articles.append(article)
    
    return unique_articles

def create_summary(title):
    """Create a brief summary from article title"""
    words = title.split()
    if len(words) > 12:
        # Take middle portion of title as summary
        summary_words = words[6:min(len(words), 15)]
        return " ".join(summary_words) + "..."
    return ""

def get_category_icon(category):
    """Get emoji icon for category"""
    icons = {
        'China Cyber': '🇨🇳',
        'Russian Cyber': '🇷🇺',
        'Iran Cyber': '🇮🇷',
        'General Cyber': '🌐',
        'Cybersecurity': '🔒',
        'Cyber Attacks': '⚠️'
    }
    return icons.get(category, '📰')

if __name__ == "__main__":
    generate_html()
