import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from datetime import datetime
import json
import random
import re

# Your exact search URL
SEARCH_URL = "https://news.google.com/search?q=china%20AND%20russian%20AND%20cyber%20when%3A24h&hl=en-US&gl=US&ceid=US%3Aen"

# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs("docs", exist_ok=True)

def is_definitely_navigation(text, element=None):
    """Strict detection of navigation items"""
    if not text:
        return True
    
    text = text.strip()
    text_lower = text.lower()
    
    # Exact navigation menu items
    nav_items = {
        'home', 'for you', 'following', 'news showcase', 'u.s.', 'world', 
        'local', 'business', 'technology', 'entertainment', 'sports', 
        'science', 'health', 'google news', 'search', 'settings', 'more',
        'latest', 'headlines', 'top stories', 'breaking news'
    }
    
    # If it's an exact match for navigation items
    if text_lower in nav_items:
        return True
    
    # If it's just one or two words and matches nav items
    if len(text.split()) <= 2 and text_lower in nav_items:
        return True
    
    # If text is too short to be a real headline
    if len(text) < 25:
        return True
    
    # If it doesn't contain common news words
    news_indicators = ['said', 'says', 'reports', 'according', 'new', 'after', 'before', 'during', 'will', 'could', 'may', 'might', 'officials', 'government', 'president', 'minister', 'company', 'announced', 'revealed', 'confirmed']
    
    # A real news headline should have at least one news indicator OR be longer than 40 chars
    has_news_words = any(word in text_lower for word in news_indicators)
    is_long_enough = len(text) > 40
    
    if not has_news_words and not is_long_enough:
        return True
    
    return False

def get_google_news_search():
    """Scrape the specific Google News search URL"""
    
    print(f"Fetching: {SEARCH_URL}")
    
    # Headers that work better with Google
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        # Add a longer delay
        time.sleep(3)
        
        response = requests.get(SEARCH_URL, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"Failed to fetch search results. Status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            return []
        
        print(f"Successfully fetched page ({len(response.content)} bytes)")
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Save the full HTML for debugging
        with open("debug_search_results.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Saved full HTML for debugging")
        
        # Remove navigation sections entirely
        nav_selectors = [
            'nav', '[role="navigation"]', '.gb_f', '.MQsxIb', 
            'header', '[data-ved]', '.FVeGwb', '.pHiOh'
        ]
        
        for selector in nav_selectors:
            for elem in soup.select(selector):
                elem.decompose()
        
        print("Removed navigation elements")
        
        # Now try to find actual news articles
        articles = []
        
        # Strategy 1: Look for article elements in the main content
        print("\n=== Strategy 1: Article elements ===")
        article_elements = soup.find_all("article")
        print(f"Found {len(article_elements)} article elements")
        
        for i, article in enumerate(article_elements):
            print(f"\nProcessing article {i+1}:")
            news_item = extract_news_from_article(article, i+1)
            if news_item:
                articles.append(news_item)
                print(f"  ✓ Added: {news_item['Title'][:60]}...")
            else:
                print(f"  ✗ Rejected article {i+1}")
        
        # Strategy 2: Look for links with article-like URLs
        if len(articles) < 3:
            print(f"\n=== Strategy 2: Article links (current: {len(articles)}) ===")
            article_links = extract_article_links(soup)
            articles.extend(article_links)
            print(f"After link extraction: {len(articles)} articles")
        
        # Strategy 3: Look for specific Google News patterns
        if len(articles) < 3:
            print(f"\n=== Strategy 3: Google News patterns (current: {len(articles)}) ===")
            gn_articles = extract_google_news_patterns(soup)
            articles.extend(gn_articles)
            print(f"After pattern extraction: {len(articles)} articles")
        
        # Remove duplicates and filter out navigation
        articles = remove_duplicates_and_nav(articles)
        
        print(f"\n=== Final Results ===")
        print(f"Found {len(articles)} valid articles after filtering")
        
        for i, article in enumerate(articles):
            print(f"{i+1}. {article['Title'][:60]}... (Source: {article['Source']})")
        
        return articles
        
    except Exception as e:
        print(f"Error fetching search results: {e}")
        import traceback
        traceback.print_exc()
        return []

def extract_news_from_article(article_elem, article_num):
    """Extract news from an article element with strict filtering"""
    try:
        # Find all links in this article
        links = article_elem.find_all("a", href=True)
        
        for link in links:
            title = link.get_text(strip=True)
            href = link.get("href")
            
            print(f"    Checking link: '{title[:40]}...' | href: {href[:50] if href else 'None'}...")
            
            # Skip if no title or href
            if not title or not href:
                print(f"      ✗ No title or href")
                continue
            
            # Skip navigation items
            if is_definitely_navigation(title, link):
                print(f"      ✗ Navigation item")
                continue
            
            # Must have article-like URL
            if not ("/articles/" in href or "/stories/" in href or "news.google.com" in href):
                print(f"      ✗ Not article URL")
                continue
            
            # Fix relative URLs
            if href.startswith("./"):
                href = "https://news.google.com" + href[1:]
            elif href.startswith("/"):
                href = "https://news.google.com" + href
            
            # Look for source in the same article
            source = find_article_source(article_elem)
            
            print(f"      ✓ Valid article found!")
            
            return {
                "Title": title,
                "Link": href,
                "Source": source,
                "Published": "Recent",
                "Scraped_At": datetime.now().isoformat()
            }
        
        return None
        
    except Exception as e:
        print(f"    Error processing article {article_num}: {e}")
        return None

def extract_article_links(soup):
    """Extract articles by looking for article-like links"""
    articles = []
    
    # Find all links that look like articles
    all_links = soup.find_all("a", href=True)
    print(f"Scanning {len(all_links)} total links...")
    
    for link in all_links:
        href = link.get("href")
        title = link.get_text(strip=True)
        
        # Must be article URL
        if not href or not ("/articles/" in href or "/stories/" in href):
            continue
        
        # Must have good title
        if not title or is_definitely_navigation(title):
            continue
        
        # Fix URL
        if href.startswith("./"):
            href = "https://news.google.com" + href[1:]
        elif href.startswith("/"):
            href = "https://news.google.com" + href
        
        articles.append({
            "Title": title,
            "Link": href,
            "Source": "Google News Search",
            "Published": "Recent",
            "Scraped_At": datetime.now().isoformat()
        })
        
        print(f"  ✓ Found via links: {title[:50]}...")
        
        if len(articles) >= 10:
            break
    
    return articles

def extract_google_news_patterns(soup):
    """Try to extract using known Google News patterns"""
    articles = []
    
    # Look for text that might be headlines
    text_elements = soup.find_all(text=True)
    
    potential_headlines = []
    for text in text_elements:
        text = text.strip()
        if (len(text) > 30 and len(text) < 200 and 
            not is_definitely_navigation(text) and
            any(keyword in text.lower() for keyword in ['china', 'russia', 'cyber', 'ukraine'])):
            potential_headlines.append(text)
    
    print(f"Found {len(potential_headlines)} potential headlines:")
    for headline in potential_headlines[:5]:
        print(f"  - {headline[:60]}...")
        
        articles.append({
            "Title": headline,
            "Link": "https://news.google.com/search?q=china%20AND%20russian%20AND%20cyber",
            "Source": "Google News Search",
            "Published": "Recent",
            "Scraped_At": datetime.now().isoformat()
        })
    
    return articles[:5]  # Limit to 5

def find_article_source(article_elem):
    """Find the source/publisher of an article"""
    # Common source selectors
    source_selectors = [
        '.wEwyrc', '.CEMjEf', '.vr1PYe', '[data-source]',
        'div[role="text"]', '.source', '.publisher'
    ]
    
    for selector in source_selectors:
        source_elem = article_elem.select_one(selector)
        if source_elem:
            source_text = source_elem.get_text(strip=True)
            if source_text and len(source_text) < 50 and not is_definitely_navigation(source_text):
                return source_text
    
    return "Google News Search"

def remove_duplicates_and_nav(articles):
    """Remove duplicates and any remaining navigation items"""
    unique_articles = []
    seen_titles = set()
    
    for article in articles:
        title = article["Title"]
        
        # Double-check it's not navigation
        if is_definitely_navigation(title):
            print(f"Filtering out navigation: {title}")
            continue
        
        # Check for duplicates
        title_normalized = title.lower().strip()
        if title_normalized in seen_titles:
            print(f"Filtering out duplicate: {title}")
            continue
        
        seen_titles.add(title_normalized)
        unique_articles.append(article)
    
    return unique_articles

def save_to_csv(news):
    """Save news data to CSV file"""
    if not news:
        print("No news data to save.")
        with open("data/latest_news.json", "w") as f:
            json.dump([], f)
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"data/google_news_search_{timestamp}.csv"
    df = pd.DataFrame(news)
    df.to_csv(filename, index=False)
    
    # Also save as latest for the website
    df.to_csv("data/latest_news.csv", index=False)
    
    # Save as JSON for web use
    with open("data/latest_news.json", "w", encoding="utf-8") as f:
        json.dump(news, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(news)} articles to {filename}")
    return filename

def main():
    """Main function to run the scraper"""
    print("Starting Google News Search scraper...")
    print("Target URL: https://news.google.com/search?q=china AND russian AND cyber when:24h")
    
    news = get_google_news_search()
    
    if news:
        save_to_csv(news)
        print(f"\nSuccessfully scraped {len(news)} articles")
        
        # Print all articles found
        print(f"\nAll articles found:")
        for i, article in enumerate(news):
            print(f"{i+1}. {article['Title']}")
            print(f"   Source: {article['Source']}")
            print(f"   Link: {article['Link']}")
            print()
    else:
        print("No valid articles found!")
        print("Check the debug_search_results.html file to see what was actually scraped.")
        with open("data/latest_news.json", "w") as f:
            json.dump([], f)

if __name__ == "__main__":
    main()
