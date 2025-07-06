import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from datetime import datetime
import json
import random
import urllib.parse

# Search query - you can modify this to search for different topics
SEARCH_QUERY = "china AND russian AND cyber"
SEARCH_TIMEFRAME = "when:24h"  # Last 24 hours

# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs("docs", exist_ok=True)

def build_google_news_search_url(query, timeframe="when:24h"):
    """Build Google News search URL"""
    base_url = "https://news.google.com/search"
    
    # Combine query with timeframe
    full_query = f"{query} {timeframe}"
    
    params = {
        'q': full_query,
        'hl': 'en-US',
        'gl': 'US',
        'ceid': 'US:en'
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return url

def is_navigation_text(text):
    """Check if text is likely navigation/menu item rather than news"""
    nav_keywords = [
        'home', 'for you', 'following', 'news showcase', 'u.s.', 'world', 
        'local', 'business', 'technology', 'entertainment', 'sports', 
        'science', 'health', 'search', 'settings', 'google news',
        'menu', 'more', 'weather', 'covid-19', 'your briefing'
    ]
    
    text_lower = text.lower().strip()
    
    # Check if it's a short navigation item
    if len(text_lower) < 15 and text_lower in nav_keywords:
        return True
    
    # Check if it's just a single word that's likely navigation
    if len(text.split()) <= 2 and text_lower in nav_keywords:
        return True
        
    return False

def is_valid_news_title(title):
    """Check if title looks like a real news headline"""
    if not title or len(title.strip()) < 20:
        return False
    
    # Skip navigation items
    if is_navigation_text(title):
        return False
    
    # Must have reasonable length
    if len(title) < 20 or len(title) > 300:
        return False
    
    # Should have multiple words
    if len(title.split()) < 4:
        return False
    
    # Skip obvious non-news items
    skip_patterns = [
        'click here', 'read more', 'subscribe', 'sign up', 'log in',
        'privacy policy', 'terms of service', 'contact us', 'about us'
    ]
    
    title_lower = title.lower()
    for pattern in skip_patterns:
        if pattern in title_lower:
            return False
    
    return True

def get_google_news_search():
    """Scrape Google News search results"""
    
    # Build the search URL
    search_url = build_google_news_search_url(SEARCH_QUERY, SEARCH_TIMEFRAME)
    print(f"Searching Google News for: {SEARCH_QUERY}")
    print(f"URL: {search_url}")
    
    # Headers to mimic a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0"
    }
    
    try:
        # Add delay to be respectful
        time.sleep(2)
        
        response = requests.get(search_url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"Failed to fetch search results. Status code: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Debug: Save the HTML to see what we're getting
        with open("debug_google_news.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        print("Saved debug HTML file")
        
        news_list = []
        
        # Strategy 1: Look for article elements with better filtering
        print("Trying to find article elements...")
        articles = soup.find_all("article")
        print(f"Found {len(articles)} article elements")
        
        for i, article in enumerate(articles):
            print(f"Processing article {i+1}")
            news_item = extract_article_info_filtered(article, i+1)
            if news_item:
                news_list.append(news_item)
                print(f"  ✓ Added: {news_item['Title'][:60]}...")
            else:
                print(f"  ✗ Skipped article {i+1}")
        
        # Strategy 2: Look for links with better filtering
        if len(news_list) < 3:
            print("Not enough articles found, trying link extraction...")
            link_articles = extract_news_links_filtered(soup)
            news_list.extend(link_articles)
        
        # Strategy 3: Try different selectors
        if len(news_list) < 3:
            print("Still not enough, trying alternative selectors...")
            alt_articles = try_alternative_selectors(soup)
            news_list.extend(alt_articles)
        
        # Remove duplicates and filter
        news_list = remove_duplicates(news_list)
        news_list = [item for item in news_list if is_valid_news_title(item['Title'])]
        
        print(f"Final result: {len(news_list)} valid articles after filtering")
        return news_list
        
    except requests.RequestException as e:
        print(f"Error fetching search results: {e}")
        return []
    except Exception as e:
        print(f"Error parsing search results: {e}")
        return []

def extract_article_info_filtered(element, article_num):
    """Extract article information with better filtering"""
    try:
        print(f"    Analyzing article {article_num}...")
        
        # Look for title - try multiple approaches
        title = None
        link = None
        
        # Try to find the main link/title
        title_selectors = [
            'h3 a',
            'h4 a', 
            'h2 a',
            'a[aria-label]',
            '.JtKRv',  # Sometimes Google uses this class
            '[role="link"]'
        ]
        
        for selector in title_selectors:
            elements = element.select(selector)
            for elem in elements:
                candidate_title = elem.get_text(strip=True)
                candidate_link = elem.get('href')
                
                print(f"      Candidate: {candidate_title[:50]}...")
                
                if is_valid_news_title(candidate_title):
                    title = candidate_title
                    if candidate_link:
                        if candidate_link.startswith("./"):
                            link = "https://news.google.com" + candidate_link[1:]
                        elif candidate_link.startswith("/"):
                            link = "https://news.google.com" + candidate_link
                        elif candidate_link.startswith("http"):
                            link = candidate_link
                    break
            
            if title:
                break
        
        if not title:
            print(f"      No valid title found")
            return None
        
        # Look for source
        source = "Google News"
        source_selectors = [
            '[data-source-name]',
            '.wEwyrc',  # Common source class
            '.CEMjEf',  # Another source class
            'div[role="text"]'
        ]
        
        for selector in source_selectors:
            source_elem = element.select_one(selector)
            if source_elem:
                source_text = source_elem.get_text(strip=True)
                if source_text and len(source_text) < 50 and not is_navigation_text(source_text):
                    source = source_text
                    break
        
        # Look for time
        time_published = "Unknown"
        time_elem = element.find("time")
        if time_elem:
            time_published = time_elem.get("datetime") or time_elem.get_text(strip=True)
        
        if title and link:
            return {
                "Title": title,
                "Link": link,
                "Source": source,
                "Published": time_published,
                "Scraped_At": datetime.now().isoformat()
            }
    
    except Exception as e:
        print(f"      Error extracting article {article_num}: {e}")
    
    return None

def extract_news_links_filtered(soup):
    """Extract news links with better filtering"""
    news_list = []
    
    print("Extracting links with filtering...")
    
    # Look for all links that might be news articles
    links = soup.find_all("a", href=True)
    print(f"Found {len(links)} total links")
    
    for link in links:
        title = link.get_text(strip=True)
        href = link.get("href")
        
        # Filter for likely news articles
        if (href and ("./articles/" in href or "/articles/" in href) and
            is_valid_news_title(title)):
            
            if href.startswith("./"):
                href = "https://news.google.com" + href[1:]
            elif href.startswith("/"):
                href = "https://news.google.com" + href
            
            news_list.append({
                "Title": title,
                "Link": href,
                "Source": "Google News",
                "Published": "Unknown",
                "Scraped_At": datetime.now().isoformat()
            })
            
            print(f"  ✓ Found via links: {title[:60]}...")
            
            if len(news_list) >= 10:  # Limit results
                break
    
    return news_list

def try_alternative_selectors(soup):
    """Try alternative CSS selectors to find news"""
    news_list = []
    
    print("Trying alternative selectors...")
    
    # Try different approaches
    selectors = [
        'div[data-n-au] a',  # Google sometimes uses this
        '[jsname] a',  # Articles with jsname
        'div[role="listitem"] a',  # List items
        '.xrnccd a',  # Another potential class
        '.JtKRv'  # Title class
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        print(f"  Trying {selector}: found {len(elements)} elements")
        
        for elem in elements:
            title = elem.get_text(strip=True)
            href = elem.get('href')
            
            if is_valid_news_title(title) and href:
                if href.startswith("./"):
                    href = "https://news.google.com" + href[1:]
                elif href.startswith("/"):
                    href = "https://news.google.com" + href
                
                news_list.append({
                    "Title": title,
                    "Link": href,
                    "Source": "Google News",
                    "Published": "Unknown",
                    "Scraped_At": datetime.now().isoformat()
                })
                
                print(f"    ✓ Found: {title[:50]}...")
                
                if len(news_list) >= 5:
                    break
        
        if news_list:
            break
    
    return news_list

def remove_duplicates(news_list):
    """Remove duplicate articles based on title similarity"""
    if not news_list:
        return []
    
    unique_news = []
    seen_titles = set()
    
    for item in news_list:
        title_lower = item["Title"].lower()
        
        # Check for exact duplicates first
        if title_lower in seen_titles:
            continue
        
        # Check for very similar titles
        is_duplicate = False
        title_words = set(title_lower.split())
        
        for seen_title in seen_titles:
            seen_words = set(seen_title.split())
            # If more than 80% of words are the same, consider it a duplicate
            if len(title_words) > 0 and len(seen_words) > 0:
                similarity = len(title_words.intersection(seen_words)) / max(len(title_words), len(seen_words))
                if similarity > 0.8:
                    is_duplicate = True
                    break
        
        if not is_duplicate:
            seen_titles.add(title_lower)
            unique_news.append(item)
    
    return unique_news

def save_to_csv(news):
    """Save news data to CSV file"""
    if not news:
        print("No news data to save.")
        # Create empty files to prevent website errors
        with open("data/latest_news.json", "w") as f:
            json.dump([], f)
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"data/google_news_search_{timestamp}.csv"
    df = pd.DataFrame(news)
    df.to_csv(filename, index=False)
    
    # Also save as latest.csv for the website
    df.to_csv("data/latest_news.csv", index=False)
    
    # Save as JSON for web use
    with open("data/latest_news.json", "w", encoding="utf-8") as f:
        json.dump(news, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(news)} articles to {filename}")
    return filename

def main():
    """Main function to run the scraper"""
    print("Starting Google News Search scraper...")
    print(f"Search query: {SEARCH_QUERY}")
    print(f"Timeframe: {SEARCH_TIMEFRAME}")
    
    news = get_google_news_search()
    
    if news:
        save_to_csv(news)
        print(f"Successfully scraped {len(news)} articles")
        
        # Print first few titles for verification
        print(f"\nFound articles about '{SEARCH_QUERY}':")
        for i, article in enumerate(news[:5]):
            print(f"{i+1}. {article['Title']}")
            print(f"   Source: {article['Source']}")
            print(f"   Link: {article['Link'][:80]}...")
            print()
    else:
        print("No valid news articles found!")
        # Create empty files to prevent website errors
        with open("data/latest_news.json", "w") as f:
            json.dump([], f)

if __name__ == "__main__":
    main()
