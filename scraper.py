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
        
        # Try multiple strategies to find articles
        news_list = []
        
        # Strategy 1: Look for article elements (most common)
        articles = soup.find_all("article")
        print(f"Found {len(articles)} article elements")
        
        for article in articles:
            news_item = extract_article_info(article)
            if news_item:
                news_list.append(news_item)
        
        # Strategy 2: Look for specific div structures
        if not news_list:
            print("Trying alternative selectors...")
            # Common Google News class patterns
            selectors = [
                'div[data-n-au]',  # Sometimes used for articles
                'div[role="article"]',
                'div[jsname]',  # Google often uses jsname
                '[data-article-id]'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                print(f"Found {len(elements)} elements with selector: {selector}")
                
                for element in elements:
                    news_item = extract_article_info(element)
                    if news_item:
                        news_list.append(news_item)
                
                if news_list:
                    break
        
        # Strategy 3: Look for links that seem like news articles
        if not news_list:
            print("Trying fallback link extraction...")
            news_list = extract_news_links(soup)
        
        # Remove duplicates
        news_list = remove_duplicates(news_list)
        
        print(f"Successfully extracted {len(news_list)} unique articles")
        return news_list
        
    except requests.RequestException as e:
        print(f"Error fetching search results: {e}")
        return []
    except Exception as e:
        print(f"Error parsing search results: {e}")
        return []

def extract_article_info(element):
    """Extract article information from an element"""
    try:
        # Look for title - try multiple approaches
        title = None
        title_selectors = [
            'h3 a',
            'h4 a', 
            'a[role="article"]',
            'a',
            'h3',
            'h4'
        ]
        
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                title = title_elem.get_text(strip=True)
                if title and len(title) > 10:  # Reasonable title length
                    break
        
        if not title:
            return None
        
        # Look for link
        link = None
        link_elem = element.find("a", href=True)
        if link_elem:
            href = link_elem.get("href")
            if href:
                if href.startswith("./"):
                    link = "https://news.google.com" + href[1:]
                elif href.startswith("/"):
                    link = "https://news.google.com" + href
                elif href.startswith("http"):
                    link = href
        
        # Look for source
        source = "Google News"
        # Try to find source info
        source_selectors = [
            '[data-source]',
            '.source',
            '[aria-label*="source"]'
        ]
        
        for selector in source_selectors:
            source_elem = element.select_one(selector)
            if source_elem:
                source_text = source_elem.get_text(strip=True)
                if source_text and len(source_text) < 50:
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
        print(f"Error extracting article info: {e}")
    
    return None

def extract_news_links(soup):
    """Fallback method to extract news links"""
    news_list = []
    
    # Look for all links that might be news articles
    links = soup.find_all("a", href=True)
    
    for link in links:
        title = link.get_text(strip=True)
        href = link.get("href")
        
        # Filter for likely news articles
        if (title and len(title) > 20 and len(title) < 200 and
            href and ("./articles/" in href or "/articles/" in href)):
            
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
            
            if len(news_list) >= 15:  # Limit results
                break
    
    return news_list

def remove_duplicates(news_list):
    """Remove duplicate articles based on title similarity"""
    if not news_list:
        return []
    
    unique_news = []
    seen_titles = set()
    
    for item in news_list:
        title_words = set(item["Title"].lower().split())
        
        # Check if this title is too similar to existing ones
        is_duplicate = False
        for seen_title in seen_titles:
            seen_words = set(seen_title.lower().split())
            # If more than 70% of words are the same, consider it a duplicate
            if len(title_words.intersection(seen_words)) / max(len(title_words), len(seen_words)) > 0.7:
                is_duplicate = True
                break
        
        if not is_duplicate:
            seen_titles.add(item["Title"])
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
        print("No news found!")
        # Create empty files to prevent website errors
        with open("data/latest_news.json", "w") as f:
            json.dump([], f)

if __name__ == "__main__":
    main()
