import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from datetime import datetime
import json

URL = "https://news.google.com/search?q=china%20AND%20russian%20AND%20cyber%20when%3A24h&hl=en-US&gl=US&ceid=US%3Aen"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs("docs", exist_ok=True)

def get_google_news():
    """Scrape Google News articles and return as list of dictionaries"""
    try:
        print("Fetching Google News...")
        response = requests.get(URL, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to fetch Google News page. Status code: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("article", class_="IBr9hb")
        
        if not articles:
            print("No articles found. The page structure might have changed.")
            return []
        
        news_list = []
        for article in articles:
            link_tag = article.find("a", class_="gPFEn")
            if not link_tag:
                continue
            
            title = link_tag.text.strip()
            href = link_tag.get("href")
            
            # Convert relative URLs to absolute
            if href and not href.startswith("http"):
                href = "https://news.google.com" + href[1:]
            
            # Try to get additional metadata
            source_tag = article.find("div", class_="vr1PYe")
            source = source_tag.text.strip() if source_tag else "Unknown"
            
            time_tag = article.find("time")
            pub_time = time_tag.get("datetime") if time_tag else "Unknown"
            
            news_list.append({
                "Title": title,
                "Link": href,
                "Source": source,
                "Published": pub_time,
                "Scraped_At": datetime.now().isoformat()
            })
        
        return news_list
    
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return []
    except Exception as e:
        print(f"Error parsing the page: {e}")
        return []

def save_to_csv(news):
    """Save news data to CSV file"""
    if not news:
        print("No news data to save.")
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"data/google_news_{timestamp}.csv"
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
    print("Starting Google News scraper...")
    news = get_google_news()
    
    if news:
        save_to_csv(news)
        print(f"Successfully scraped {len(news)} articles")
    else:
        print("No news found or error occurred!")
        # Create empty files to prevent website errors
        with open("data/latest_news.json", "w") as f:
            json.dump([], f)

if __name__ == "__main__":
    main()
