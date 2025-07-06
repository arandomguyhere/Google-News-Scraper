import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from datetime import datetime
import json
import random

# Google News Topic IDs - these are stable identifiers
TOPIC_URLS = [
    {
        "name": "U.S. News",
        "url": "https://news.google.com/topics/CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE?hl=en-US&gl=US&ceid=US%3Aen"
    },
    {
        "name": "Business News", 
        "url": "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen"
    },
    {
        "name": "Technology News",
        "url": "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB?hl=en-US&gl=US&ceid=US%3Aen"
    }
]

# Keywords to filter for relevant articles
FILTER_KEYWORDS = ["china", "russia", "cyber", "ukraine", "security", "defense"]

# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs("docs", exist_ok=True)

def get_google_news_topics():
    """Scrape multiple Google News topics and filter for relevant articles"""
    all_news = []
    
    for topic in TOPIC_URLS:
        print(f"\n=== Scraping {topic['name']} ===")
        articles = scrape_topic_page(topic["url"], topic["name"])
        
        # Filter articles for our keywords
        filtered_articles = filter_articles_by_keywords(articles, FILTER_KEYWORDS)
        
        print(f"Found {len(articles)} total articles, {len(filtered_articles)} relevant")
        all_news.extend(filtered_articles)
        
        # Be respectful with delays
        time.sleep(random.uniform(2, 4))
    
    # Remove duplicates
    unique_news = remove_duplicates(all_news)
    print(f"\nTotal unique relevant articles: {len(unique_news)}")
    
    return unique_news

def scrape_topic_page(url, topic_name):
    """Scrape a specific Google News topic page"""
    # Rotate through different user agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"Failed to fetch {topic_name}. Status code: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Save debug HTML for the first topic
        if topic_name == "U.S. News":
            with open("debug_topic_page.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())
            print("Saved debug HTML file")
        
        # Try multiple strategies to extract articles
        articles = []
        
        # Strategy 1: Look for article elements
        article_elements = soup.find_all("article")
        print(f"Found {len(article_elements)} article elements")
        
        for article in article_elements:
            article_info = extract_article_from_element(article, topic_name)
            if article_info:
                articles.append(article_info)
        
        # Strategy 2: Look for common link patterns in Google News
        if len(articles) < 5:
            print("Trying alternative link extraction...")
            link_articles = extract_from_links(soup, topic_name)
            articles.extend(link_articles)
        
        # Strategy 3: Look for specific Google News structures
        if len(articles) < 5:
            print("Trying Google News specific selectors...")
            gn_articles = extract_with_google_selectors(soup, topic_name)
            articles.extend(gn_articles)
        
        return articles
        
    except Exception as e:
        print(f"Error scraping {topic_name}: {e}")
        return []

def extract_article_from_element(element, topic_name):
    """Extract article info from an article element"""
    try:
        # Look for title and link
        title = None
        link = None
        
        # Common selectors for titles in Google News
        title_selectors = [
            'h3 a', 'h4 a', 'h2 a',
            'a[aria-label]',
            '.JtKRv a',  # Google News specific
            '.ipQwMb a',  # Another GN class
            '.WwrzSb a'   # Another potential class
        ]
        
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                candidate_title = title_elem.get_text(strip=True)
                candidate_link = title_elem.get('href')
                
                if candidate_title and len(candidate_title) > 15 and not is_navigation_text(candidate_title):
                    title = candidate_title
                    link = candidate_link
                    break
        
        if not title:
            return None
        
        # Fix relative URLs
        if link:
            if link.startswith("./"):
                link = "https://news.google.com" + link[1:]
            elif link.startswith("/"):
                link = "https://news.google.com" + link
        
        # Look for source
        source = topic_name
        source_selectors = [
            '.wEwyrc', '.CEMjEf', '.vr1PYe',
            '[data-source-name]',
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
        time_published = "Recent"
        time_elem = element.find("time")
        if time_elem:
            time_published = time_elem.get("datetime") or time_elem.get_text(strip=True)
        
        return {
            "Title": title,
            "Link": link,
            "Source": source,
            "Published": time_published,
            "Scraped_At": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error extracting from element: {e}")
        return None

def extract_from_links(soup, topic_name):
    """Extract articles from all links on the page"""
    articles = []
    
    # Find all links that might be articles
    links = soup.find_all("a", href=True)
    
    for link in links:
        href = link.get("href")
        title = link.get_text(strip=True)
        
        # Filter for article-like links
        if (href and title and 
            len(title) > 20 and len(title) < 200 and
            not is_navigation_text(title) and
            ("./articles/" in href or "/articles/" in href or "stories/" in href)):
            
            # Fix URL
            if href.startswith("./"):
                href = "https://news.google.com" + href[1:]
            elif href.startswith("/"):
                href = "https://news.google.com" + href
            
            articles.append({
                "Title": title,
                "Link": href,
                "Source": topic_name,
                "Published": "Recent",
                "Scraped_At": datetime.now().isoformat()
            })
            
            if len(articles) >= 10:  # Limit to avoid too many
                break
    
    return articles

def extract_with_google_selectors(soup, topic_name):
    """Try Google News specific CSS selectors"""
    articles = []
    
    # Known Google News selectors (these change frequently)
    selectors = [
        '[jsname] a[href*="articles"]',
        '[data-n-au] a',
        '.xrnccd a',
        '.JtKRv',
        '.ipQwMb a'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        print(f"Selector '{selector}' found {len(elements)} elements")
        
        for elem in elements:
            title = elem.get_text(strip=True)
            href = elem.get('href')
            
            if title and href and len(title) > 20 and not is_navigation_text(title):
                if href.startswith("./"):
                    href = "https://news.google.com" + href[1:]
                elif href.startswith("/"):
                    href = "https://news.google.com" + href
                
                articles.append({
                    "Title": title,
                    "Link": href,
                    "Source": topic_name,
                    "Published": "Recent",
                    "Scraped_At": datetime.now().isoformat()
                })
                
                if len(articles) >= 5:
                    break
        
        if articles:
            break
    
    return articles

def is_navigation_text(text):
    """Check if text is navigation/menu rather than news"""
    nav_items = [
        'home', 'for you', 'following', 'u.s.', 'world', 'local', 
        'business', 'technology', 'entertainment', 'sports', 'science', 
        'health', 'search', 'settings', 'google news', 'more'
    ]
    
    text_lower = text.lower().strip()
    return (len(text_lower) < 15 and text_lower in nav_items) or len(text.split()) <= 1

def filter_articles_by_keywords(articles, keywords):
    """Filter articles that contain relevant keywords"""
    filtered = []
    
    for article in articles:
        title_lower = article["Title"].lower()
        
        # Check if any keyword appears in title
        for keyword in keywords:
            if keyword.lower() in title_lower:
                filtered.append(article)
                break  # Don't add duplicates
    
    return filtered

def remove_duplicates(articles):
    """Remove duplicate articles"""
    unique_articles = []
    seen_titles = set()
    
    for article in articles:
        title_normalized = article["Title"].lower().strip()
        
        if title_normalized not in seen_titles:
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
    filename = f"data/google_news_topics_{timestamp}.csv"
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
    print("Starting Google News Topics scraper...")
    print("Targeting: U.S., Business, and Technology news")
    print(f"Filtering for keywords: {', '.join(FILTER_KEYWORDS)}")
    
    news = get_google_news_topics()
    
    if news:
        save_to_csv(news)
        print(f"\nSuccessfully scraped {len(news)} relevant articles")
        
        # Print first few titles for verification
        print(f"\nSample articles found:")
        for i, article in enumerate(news[:5]):
            print(f"{i+1}. {article['Title']}")
            print(f"   Source: {article['Source']}")
            print()
    else:
        print("No relevant articles found!")
        with open("data/latest_news.json", "w") as f:
            json.dump([], f)

if __name__ == "__main__":
    main()
