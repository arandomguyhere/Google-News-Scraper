import urllib.request
import urllib.parse
from bs4 import BeautifulSoup as Soup
import pandas as pd
import os
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse, urlunparse
import json
import random

# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs("docs", exist_ok=True)


def define_date(date):
    """Convert relative date strings to datetime objects"""
    if not date:
        return None
    try:
        dl = date.lower()
        if "minute" in dl:
            return datetime.now() - timedelta(minutes=int(dl.split()[0]))
        if "hour" in dl:
            return datetime.now() - timedelta(hours=int(dl.split()[0]))
        if "day" in dl:
            return datetime.now() - timedelta(days=int(dl.split()[0]))
        if "week" in dl:
            return datetime.now() - timedelta(weeks=int(dl.split()[0]))
        if "yesterday" in dl:
            return datetime.now() - timedelta(days=1)
        return datetime.now()
    except:
        return datetime.now()


def clean_img_url(src):
    """Process and validate image URL from Google News"""
    if not src:
        return None
    if src.startswith("//"):
        return "https:" + src
    if src.startswith("/"):
        return "https://news.google.com" + src
    if src.startswith("data:"):
        return None
    return src


def normalize_url(url):
    """Normalize URL by removing amp and standardizing format"""
    try:
        parsed = urlparse(url)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path.replace("/amp", ""), "", "", ""))
    except:
        return url


class MultiSearchGoogleNews:
    def __init__(self, lang="en-US", gl="US", ceid="US:en"):
        self.lang = lang
        self.gl = gl
        self.ceid = ceid
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        self.all_results = []

    def parse_article(self, card, category):
        """Parse a single article card and extract all relevant data"""
        title = None
        for sel in ["h3", "h4", "a[role='heading']", "a[aria-level='2']"]:
            el = card.select_one(sel)
            if el:
                title = el.get_text(strip=True)
                if title:
                    break

        if not title:
            texts = [a.get_text(strip=True) for a in card.select("a[href]") if a.get_text(strip=True)]
            if texts:
                title = max(texts, key=len)

        if not title or len(title) < 5:
            return None

        # Skip navigation items
        nav_terms = ['home', 'for you', 'following', 'u.s.', 'world', 'local',
                     'business', 'technology', 'entertainment', 'sports',
                     'science', 'health', 'google news', 'more']
        if title.lower().strip() in nav_terms:
            return None

        a = card.select_one("a[href]")
        if not a:
            return None
        href = a.get("href", "")

        if href.startswith("./"):
            link = "https://news.google.com" + href[1:]
        elif href.startswith("/"):
            link = "https://news.google.com" + href
        else:
            link = href

        link = normalize_url(link)

        t = card.select_one("time")
        date_text = t.get_text(strip=True) if t else "Recent"
        dt = define_date(date_text)

        source = None
        for sp in card.select("span"):
            txt = sp.get_text(strip=True)
            if txt and len(txt) < 45 and "ago" not in txt.lower():
                source = txt
                break

        img = card.select_one("img")
        img = clean_img_url(img.get("src")) if img else None

        return {
            "title": title,
            "link": link,
            "media": source or category,
            "date": date_text,
            "datetime": dt,
            "img": img,
            "search_category": category,
        }

    def select_cards(self, soup):
        """Select article cards using multiple selectors"""
        selectors = ["article", "c-wiz[jsrenderer]", "div.Vd5Uad", "div.SoaBEf", "div.XlKvRb"]
        for sel in selectors:
            cards = soup.select(sel)
            if cards:
                return cards
        return []

    def search_single_query(self, query, category):
        """Search Google News for a single query"""
        print(f"\n{'='*50}")
        print(f"Searching: {category}")
        print(f"Query: {query}")
        print(f"{'='*50}")

        encoded = urllib.parse.quote(query)
        url = f"https://news.google.com/search?q={encoded}&hl={self.lang}&gl={self.gl}&ceid={self.ceid}"

        print(f"URL: {url}")

        try:
            req = urllib.request.Request(url, headers=self.headers)
            html = urllib.request.urlopen(req, timeout=30).read()
            soup = Soup(html, "html.parser")
            cards = self.select_cards(soup)

            print(f"Found {len(cards)} article containers")

            out = []
            for c in cards[:12]:
                article = self.parse_article(c, category)
                if article:
                    print(f"  ✓ Found: {article['title'][:60]}... (Source: {article['media']})")
                    out.append(article)

            print(f"✓ {category}: {len(out)} valid articles")
            return out

        except Exception as e:
            print(f"✗ {category}: Error during search: {e}")
            return []

    def run_all_searches(self):
        """Run all the individual searches"""
        print("Starting multi-search Google News scraping...")

        searches = [
            # Core cyber operations
            ("China cyber when:24h", "China Cyber"),
            ("Russian cyber when:24h", "Russian Cyber"),
            ("DPRK cyber when:24h", "DPRK Cyber"),
            ("North Korea cyber when:24h", "North Korea Cyber"),
            ("state-sponsored hackers when:24h", "state-sponsored Cyber"),
            ("Iran cyber when:24h", "Iran Cyber"),
            ("cybersecurity when:24h", "Cybersecurity"),
            ("Hackers when:24h", "Hackers"),
            ("cyber attack when:24h", "Cyber Attacks"),

            # APT Groups and Threat Actors
            ("Advanced Persistent Threat when:24h", "APT Groups"),
            ("Salt Typhoon when:24h", "Advanced Threats"),
            ("ransomware when:24h", "Ransomware"),

            # Critical Infrastructure
            ("critical infrastructure cyber when:24h", "Critical Infrastructure"),
            ("power grid cyber when:24h", "Energy Security"),
            ("supply chain attack when:24h", "Supply Chain"),

            # Vulnerabilities and Exploits
            ("zero day exploit when:24h", "Zero Days"),
            ("CVE when:24h", "Vulnerabilities"),
            ("Ivanti when:24h", "VPN Security"),

            # Emerging Technologies
            ("AI security when:24h", "AI Security"),
            ("quantum computing cyber when:24h", "Quantum Threats"),
            ("blockchain security when:24h", "Blockchain Security"),

            # Geopolitical Cyber
            ("Taiwan cyber when:24h", "Taiwan Security"),
            ("Ukraine cyber when:24h", "Ukraine Conflict"),
            ("Israel cyber when:24h", "Middle East Cyber"),

            # Attack Methods
            ("phishing when:24h", "Phishing"),
            ("malware when:24h", "Malware"),
            ("social engineering when:24h", "Social Engineering"),

            # Industries and Sectors
            ("healthcare cyber when:24h", "Healthcare Security"),
            ("financial cyber when:24h", "Financial Security"),
            ("maritime cyber when:24h", "Maritime Security"),

            # Technology Targets
            ("Huawei security when:24h", "Tech Companies"),
            ("5G security when:24h", "5G Networks"),
            ("IoT security when:24h", "IoT Security"),

            # Site-specific searches
            ("site:ft.com cyber when:24h", "FT Cyber"),
            ("site:theregister.com security when:24h", "Register Security"),
            ("site:forbes.com cybersecurity when:24h", "Forbes Cyber"),
            ("site:wsj.com cyber when:24h", "WSJ Cyber"),
            ("site:reuters.com cyber when:24h", "Reuters Cyber"),
            ("site:bloomberg.com cybersecurity when:24h", "Bloomberg Cyber"),
            ("site:techcrunch.com security when:24h", "TechCrunch Security"),
            ("site:wired.com cyber when:24h", "Wired Cyber"),
            ("site:krebsonsecurity.com when:24h", "Krebs Security"),
            ("site:darkreading.com when:24h", "Dark Reading"),
            ("site:securityweek.com when:24h", "Security Week"),
        ]

        all_articles = []

        for query, search_name in searches:
            articles = self.search_single_query(query, search_name)
            all_articles.extend(articles)
            time.sleep(random.uniform(0.4, 1.0))

        unique_articles = self.remove_duplicates(all_articles)

        print(f"\n{'='*50}")
        print(f"FINAL RESULTS")
        print(f"{'='*50}")
        print(f"Total articles found: {len(all_articles)}")
        print(f"Unique articles after deduplication: {len(unique_articles)}")

        # Show breakdown by category
        categories = {}
        for article in unique_articles:
            cat = article.get('search_category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1

        print(f"\nBreakdown by category:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count} articles")

        self.all_results = unique_articles
        return unique_articles

    def remove_duplicates(self, articles):
        """Remove duplicate articles based on title similarity"""
        if not articles:
            return []

        unique_articles = []
        seen_titles = set()

        for article in articles:
            title = article['title'].lower().strip()
            title_words = set(title.split())

            is_duplicate = False
            for seen_title in seen_titles:
                seen_words = set(seen_title.split())
                if len(title_words) > 0 and len(seen_words) > 0:
                    similarity = len(title_words.intersection(seen_words)) / max(len(title_words), len(seen_words))
                    if similarity > 0.7:
                        is_duplicate = True
                        break

            if not is_duplicate:
                seen_titles.add(title)
                unique_articles.append(article)

        return unique_articles


def scrape_google_news_multi():
    """Main scraping function for multiple searches"""
    searcher = MultiSearchGoogleNews()
    articles = searcher.run_all_searches()

    formatted_articles = []
    for article in articles:
        formatted_articles.append({
            "Title": article['title'],
            "Link": article['link'] or "https://news.google.com",
            "Source": article['media'] or "Google News",
            "Published": article['date'] or "Recent",
            "Category": article.get('search_category', 'General'),
            "img": article.get('img'),
            "Scraped_At": datetime.now().isoformat()
        })

    return formatted_articles


def save_to_csv(news):
    """Save news data to CSV file"""
    if not news:
        print("No news data to save.")
        with open("data/latest_news.json", "w") as f:
            json.dump([], f)
        return None

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"data/google_news_multi_{timestamp}.csv"
    df = pd.DataFrame(news)
    df.to_csv(filename, index=False)

    df.to_csv("data/latest_news.csv", index=False)

    with open("data/latest_news.json", "w", encoding="utf-8") as f:
        json.dump(news, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(news)} articles to {filename}")
    return filename


def main():
    """Main function to run the scraper"""
    print("Starting Comprehensive Multi-Search Google News scraper...")

    try:
        news = scrape_google_news_multi()

        if news:
            save_to_csv(news)
            print(f"\nSuccessfully processed {len(news)} articles")

            print(f"\nSample articles found:")
            for i, article in enumerate(news[:5]):
                print(f"{i+1}. {article['Title']}")
                print(f"   Source: {article['Source']}")
                print(f"   Category: {article['Category']}")
                print()

            if len(news) > 5:
                print(f"... and {len(news) - 5} more articles")
        else:
            print("No articles found!")
            with open("data/latest_news.json", "w") as f:
                json.dump([], f)

    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()
        with open("data/latest_news.json", "w") as f:
            json.dump([], f)


if __name__ == "__main__":
    main()
