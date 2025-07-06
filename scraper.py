import requests
import urllib.request
import dateparser
import copy
from bs4 import BeautifulSoup as Soup
from dateutil.parser import parse
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import os
import time
import json
import logging

# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs("docs", exist_ok=True)

def lexical_date_parser(date_to_check):
    if date_to_check=='':
        return ('',None)
    datetime_tmp=None
    date_tmp=copy.copy(date_to_check)
    try:
        date_tmp = date_tmp[date_tmp.rfind('..')+2:]
        datetime_tmp=dateparser.parse(date_tmp)
    except:
        date_tmp = None
        datetime_tmp = None

    if datetime_tmp==None:
        date_tmp=date_to_check
    else:
        datetime_tmp=datetime_tmp.replace(tzinfo=None)

    if date_tmp and len(date_tmp) > 0 and date_tmp[0]==' ':
        date_tmp=date_tmp[1:]
    return date_tmp,datetime_tmp

def define_date(date):
    if not date:
        return None
    months = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Sept':9,'Oct':10,'Nov':11,'Dec':12, '01':1, '02':2, '03':3, '04':4, '05':5, '06':6, '07':7, '08':8, '09':9, '10':10, '11':11, '12':12}
    try:
        if ' ago' in date.lower():
            q = int(date.split()[-3])
            if 'minutes' in date.lower() or 'mins' in date.lower():
                return datetime.datetime.now() + relativedelta(minutes=-q)
            elif 'hour' in date.lower():
                return datetime.datetime.now() + relativedelta(hours=-q)
            elif 'day' in date.lower():
                return datetime.datetime.now() + relativedelta(days=-q)
            elif 'week' in date.lower():
                return datetime.datetime.now() + relativedelta(days=-7*q)
            elif 'month' in date.lower():
                return datetime.datetime.now() + relativedelta(months=-q)
        elif 'yesterday' in date.lower():
            return datetime.datetime.now() + relativedelta(days=-1)
        else:
            date_list = date.replace('/',' ').split(' ')
            if len(date_list) == 2:
                date_list.append(datetime.datetime.now().year)
            elif len(date_list) == 3:
                if date_list[0] == '':
                    date_list[0] = '1'
            return datetime.datetime(day=int(date_list[0]), month=months[date_list[1]], year=int(date_list[2]))
    except:
        return None

class GoogleNews:
    def __init__(self, lang="en", period="", start="", end="", encode="utf-8", region=None):
        self.__texts = []
        self.__links = []
        self.__results = []
        self.__totalcount = 0
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.__lang = lang
        if region:
            self.accept_language = lang + '-' + region + ',' + lang + ';q=0.9'
            self.headers = {'User-Agent': self.user_agent, 'Accept-Language': self.accept_language}
        else:
            self.headers = {'User-Agent': self.user_agent}
        self.__period = period
        self.__start = start
        self.__end = end
        self.__encode = encode
        self.__exception = False

    def search(self, key):
        """Search for a term in Google News"""
        self.__key = key
        if self.__encode != "":
            self.__key = urllib.request.quote(self.__key.encode(self.__encode))
        self.get_news()

    def get_news(self, key="", deamplify=False):
        """Get news from Google News using the search method"""
        if key != '':
            search_query = key
        else:
            search_query = getattr(self, '_GoogleNews__key', '')
        
        if self.__period != "":
            search_query += f" when:{self.__period}"
        
        # URL encode the search query
        encoded_query = urllib.request.quote(search_query.encode(self.__encode))
        
        # Build the Google News URL
        self.url = f'https://news.google.com/search?q={encoded_query}&hl={self.__lang.lower()}'
        
        print(f"Searching Google News: {self.url}")
        
        try:
            self.req = urllib.request.Request(self.url, headers=self.headers)
            self.response = urllib.request.urlopen(self.req, timeout=30)
            self.page = self.response.read()
            self.content = Soup(self.page, "html.parser")
            
            # Save debug HTML
            with open("debug_googlenews_library.html", "w", encoding="utf-8") as f:
                f.write(str(self.content))
            print("Saved debug HTML file")
            
            articles = self.content.select('article')
            print(f"Found {len(articles)} article elements")
            
            for i, article in enumerate(articles):
                print(f"Processing article {i+1}...")
                try:
                    # Extract title - try multiple methods
                    title = None
                    try:
                        title = article.find('h3').get_text(strip=True)
                    except:
                        try:
                            title = article.find('h4').get_text(strip=True)
                        except:
                            try:
                                title = article.find('a').get_text(strip=True)
                            except:
                                title = None
                    
                    if not title or len(title) < 10:
                        print(f"  Skipping - no valid title")
                        continue
                    
                    # Extract link
                    link = None
                    try:
                        link_elem = article.find('a')
                        if link_elem and link_elem.get('href'):
                            href = link_elem.get('href')
                            if href.startswith('./'):
                                link = 'https://news.google.com' + href[1:]
                            elif href.startswith('/'):
                                link = 'https://news.google.com' + href
                            else:
                                link = href
                    except:
                        link = None
                    
                    # Extract date
                    date = None
                    datetime_obj = None
                    try:
                        time_elem = article.find("time")
                        if time_elem:
                            date = time_elem.get_text(strip=True)
                            datetime_chars = time_elem.get('datetime')
                            if datetime_chars:
                                datetime_obj = parse(datetime_chars).replace(tzinfo=None)
                            else:
                                datetime_obj = define_date(date)
                    except:
                        date = None
                        datetime_obj = None
                    
                    # Extract source/media
                    media = None
                    try:
                        # Try to find source information
                        source_candidates = article.find_all(['span', 'div', 'a'])
                        for candidate in source_candidates:
                            text = candidate.get_text(strip=True)
                            if text and len(text) < 50 and text not in title:
                                # Check if it looks like a news source
                                if any(word in text.lower() for word in ['news', 'times', 'post', 'bbc', 'cnn', 'reuters', 'ap ', 'reuters']):
                                    media = text
                                    break
                        if not media:
                            media = "Google News"
                    except:
                        media = "Google News"
                    
                    # Extract image
                    img = None
                    try:
                        img_elem = article.find("img")
                        if img_elem and img_elem.get("src"):
                            img_src = img_elem.get("src")
                            if img_src.startswith('//'):
                                img = 'https:' + img_src
                            elif img_src.startswith('/'):
                                img = 'https://news.google.com' + img_src
                            else:
                                img = img_src
                    except:
                        img = None
                    
                    # Only add if we have a title and it contains our keywords
                    if title and any(keyword in title.lower() for keyword in ['china', 'russia', 'cyber', 'ukraine', 'security']):
                        print(f"  ✓ Found relevant article: {title[:60]}...")
                        
                        self.__texts.append(title)
                        self.__links.append(link)
                        self.__results.append({
                            'title': title,
                            'desc': None,  # Description not available in this format
                            'date': date,
                            'datetime': datetime_obj,
                            'link': link,
                            'img': img,
                            'media': media,
                            'site': media,
                            'reporter': None
                        })
                    else:
                        print(f"  ✗ Skipping - not relevant: {title[:40] if title else 'No title'}...")
                        
                except Exception as e_article:
                    print(f"  Error processing article {i+1}: {e_article}")
                    continue
            
            self.response.close()
            print(f"Successfully processed {len(self.__results)} relevant articles")
            
        except Exception as e_parser:
            print(f"Error during scraping: {e_parser}")
            if self.__exception:
                raise Exception(e_parser)

    def results(self, sort=False):
        """Return the results"""
        results = self.__results
        if sort and results:
            try:
                results.sort(key=lambda x: x['datetime'] if x['datetime'] else datetime.datetime.min, reverse=True)
            except Exception as e_sort:
                print(f"Error sorting: {e_sort}")
        return results

    def clear(self):
        """Clear all results"""
        self.__texts = []
        self.__links = []
        self.__results = []
        self.__totalcount = 0

def scrape_google_news():
    """Main scraping function"""
    print("Starting Google News scraping with proven library method...")
    
    # Initialize Google News scraper
    gn = GoogleNews(lang='en', period='1d')  # Last 24 hours
    
    # Search for our specific query
    search_query = "china AND russia AND cyber"
    print(f"Searching for: {search_query}")
    
    gn.search(search_query)
    
    # Get results
    results = gn.results(sort=True)
    
    # Convert to our expected format
    articles = []
    for result in results:
        articles.append({
            "Title": result['title'],
            "Link": result['link'] or "https://news.google.com",
            "Source": result['media'] or "Google News",
            "Published": result['date'] or "Recent",
            "Scraped_At": datetime.datetime.now().isoformat()
        })
    
    return articles

def save_to_csv(news):
    """Save news data to CSV file"""
    if not news:
        print("No news data to save.")
        with open("data/latest_news.json", "w") as f:
            json.dump([], f)
        return None
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"data/google_news_library_{timestamp}.csv"
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
    print("Starting Google News Library scraper...")
    print("Target: china AND russia AND cyber (last 24 hours)")
    
    try:
        # Run the scraper
        news = scrape_google_news()
        
        if news:
            save_to_csv(news)
            print(f"\nSuccessfully scraped {len(news)} articles")
            
            # Print articles found
            print(f"\nArticles found:")
            for i, article in enumerate(news):
                print(f"{i+1}. {article['Title']}")
                print(f"   Source: {article['Source']}")
                print(f"   Link: {article['Link']}")
                print()
        else:
            print("No articles found!")
            with open("data/latest_news.json", "w") as f:
                json.dump([], f)
                
    except Exception as e:
        print(f"Error in main: {e}")
        with open("data/latest_news.json", "w") as f:
            json.dump([], f)

if __name__ == "__main__":
    main()
