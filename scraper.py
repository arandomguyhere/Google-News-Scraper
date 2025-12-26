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

# ---------------------------------------------------------
# SEARCH QUERIES - Comprehensive source list
# ---------------------------------------------------------
SEARCH_QUERIES = [
    # MAINSTREAM MEDIA
    ("site:wsj.com cyber when:24h", "WSJ Cyber"),
    ("site:ft.com cyber when:24h", "FT Cyber"),
    ("site:reuters.com cyber when:24h", "Reuters Cyber"),
    ("site:nytimes.com cyber when:24h", "NYT Cyber"),
    ("site:france24.com cyber when:24h", "France24 Cyber"),
    ("site:independent.co.uk cyber when:24h", "Independent Cyber"),
    ("site:smh.com.au cyber when:24h", "SMH Cyber"),
    ("site:chosun.com cyber when:24h", "Chosun Cyber"),
    ("site:aol.com cyber when:24h", "AOL Cyber"),
    ("site:msn.com cyber when:24h", "MSN Cyber"),
    ("site:express.co.uk cyber when:24h", "Daily Express Cyber"),
    ("site:bloomberg.com cybersecurity when:24h", "Bloomberg Cyber"),
    ("site:techcrunch.com security when:24h", "TechCrunch Security"),
    ("site:wired.com cyber when:24h", "Wired Cyber"),
    ("site:forbes.com cybersecurity when:24h", "Forbes Cyber"),

    # TECH/SECURITY PUBLICATIONS
    ("site:therecord.media when:24h", "The Record"),
    ("site:theregister.com security when:24h", "The Register"),
    ("site:bleepingcomputer.com when:24h", "Bleeping Computer"),
    ("site:thehackernews.com when:24h", "The Hacker News"),
    ("site:gbhackers.com when:24h", "GBHackers"),
    ("site:securityweek.com when:24h", "SecurityWeek"),
    ("site:cybernews.com when:24h", "CyberNews"),
    ("site:cyberscoop.com when:24h", "CyberScoop"),
    ("site:cybersecuritydive.com when:24h", "Cybersecurity Dive"),
    ("site:darkreading.com when:24h", "Dark Reading"),
    ("site:scworld.com when:24h", "SC World"),
    ("site:csoonline.com when:24h", "CSO Online"),
    ("site:cpomagazine.com when:24h", "CPO Magazine"),
    ("site:bankinfosecurity.com when:24h", "Bank Info Security"),
    ("site:computerweekly.com cyber when:24h", "Computer Weekly"),
    ("site:itpro.com security when:24h", "ITPro"),
    ("site:redhotcyber.com when:24h", "Red Hot Cyber"),
    ("site:tomshardware.com security when:24h", "Tom's Hardware"),
    ("site:webpronews.com cyber when:24h", "Web Pro News"),
    ("site:krebsonsecurity.com when:24h", "Krebs on Security"),
    ("site:schneier.com when:24h", "Schneier on Security"),

    # VENDOR RESEARCH / THREAT INTEL
    ("site:trendmicro.com research when:24h", "Trend Micro"),
    ("site:elastic.co security-labs when:24h", "Elastic Security Labs"),
    ("site:kaspersky.com securelist when:24h", "Kaspersky"),
    ("site:mandiant.com blog when:24h", "Mandiant"),
    ("site:wiz.io blog when:24h", "Wiz"),
    ("site:huntress.com blog when:24h", "Huntress"),
    ("site:trailofbits.com when:24h", "Trail of Bits"),
    ("site:unit42.paloaltonetworks.com when:24h", "Unit 42"),
    ("site:crowdstrike.com blog when:24h", "CrowdStrike"),
    ("site:sentinelone.com blog when:24h", "SentinelOne"),

    # CHINESE SECURITY SITES
    ("site:freebuf.com when:24h", "Freebuf"),

    # REGIONAL / INTERNATIONAL
    ("site:scmp.com cyber when:24h", "SCMP"),
    ("site:koreatimes.co.kr cyber when:24h", "Korea Times"),
    ("site:kyivindependent.com cyber when:24h", "Kyiv Independent"),
    ("site:united24media.com when:24h", "United 24"),
    ("site:unn.ua cyber when:24h", "UNN"),
    ("site:nst.com.my cyber when:24h", "New Straits Times"),
    ("site:wionews.com cyber when:24h", "WION News"),
    ("site:ibtimes.com cyber when:24h", "IBT"),
    ("site:intelligenceonline.com when:24h", "Intelligence Online"),
    ("site:globalbankingandfinance.com cyber when:24h", "Global Banking Finance"),

    # GOVERNMENT / THINK TANKS / POLICY
    ("site:fdd.org cyber when:24h", "FDD"),
    ("site:justsecurity.org cyber when:24h", "Just Security"),
    ("site:smallwarsjournal.com cyber when:24h", "Small Wars Journal"),
    ("site:kharon.com when:24h", "Kharon"),
    ("site:thedefensepost.com cyber when:24h", "Defense Post"),
    ("site:nationalinterest.org cyber when:24h", "National Interest"),
    ("site:realcleardefense.com cyber when:24h", "Real Clear Defense"),
    ("site:fpif.org cyber when:24h", "FPIF"),
    ("site:aspi.org.au cyber when:24h", "ASPI"),
    ("site:netaskari.com when:24h", "NetAskari"),

    # LEGAL / REGULATORY
    ("site:iclg.com cyber when:24h", "ICLG"),
    ("site:mayerbrown.com cyber when:24h", "Mayer Brown"),

    # SUBSTACKS - CHINA/ASIA
    ("site:aisafetychina.substack.com when:24h", "AI Safety China"),
    ("site:chinapolicy.substack.com when:24h", "China Policy"),
    ("site:chinabossnews.substack.com when:24h", "China Boss News"),
    ("site:trackingpeoplesdaily.substack.com when:24h", "Tracking People's Daily"),
    ("site:chinai.substack.com when:24h", "ChinAI"),
    ("site:theaseanchair.substack.com when:24h", "ASEAN Chair"),

    # SUBSTACKS - GEOPOLITICS/DEFENSE
    ("site:phillipspobrien.substack.com when:24h", "Phillips O'Brien"),
    ("site:grayandgritty.substack.com when:24h", "Gray and Gritty"),
    ("site:thelinchpin.substack.com when:24h", "The Linchpin"),
    ("site:richardgibson.substack.com when:24h", "Richard Gibson"),
    ("site:southpacifictides.substack.com when:24h", "South Pacific Tides"),
    ("site:sixtydegreesnorth.substack.com when:24h", "Sixty Degrees North"),

    # SUBSTACKS - CYBER/TECH
    ("site:cisotradecraft.substack.com when:24h", "CISO Tradecraft"),
    ("site:cybermaterial.substack.com when:24h", "Cybermaterial"),
    ("site:eyeoncyber.substack.com when:24h", "Eye on Cyber"),
    ("site:pascal.substack.com when:24h", "Pascal"),
    ("site:sebastianbarros.substack.com when:24h", "Sebastian Barros"),
    ("site:therisingtide.substack.com when:24h", "The Rising Tide"),
    ("site:merylnass.substack.com when:24h", "Meryl Nass"),
    ("site:zoescaman.substack.com when:24h", "Zoe Scaman"),

    # PODCASTS / MEDIA
    ("site:risky.biz when:24h", "Risky Business"),
    ("site:lawfaremedia.org when:24h", "Lawfare"),

    # ---------------------------------------------------------
    # TOPIC-BASED SEARCHES - Nation State Actors
    # ---------------------------------------------------------
    ("China cyber when:24h", "China Cyber"),
    ("Russia cyber when:24h", "Russia Cyber"),
    ("DPRK cyber when:24h", "DPRK Cyber"),
    ("North Korea cyber when:24h", "North Korea Cyber"),
    ("Iran cyber when:24h", "Iran Cyber"),
    ("state-sponsored hackers when:24h", "State-Sponsored Cyber"),

    # ---------------------------------------------------------
    # TOPIC-BASED SEARCHES - Threat Types
    # ---------------------------------------------------------
    ("ransomware when:24h", "Ransomware"),
    ("zero day exploit when:24h", "Zero Days"),
    ("CVE vulnerability when:24h", "Vulnerabilities"),
    ("APT threat actor when:24h", "APT Groups"),
    ("Advanced Persistent Threat when:24h", "Advanced Threats"),
    ("Salt Typhoon when:24h", "Salt Typhoon"),
    ("phishing when:24h", "Phishing"),
    ("malware when:24h", "Malware"),
    ("social engineering when:24h", "Social Engineering"),

    # ---------------------------------------------------------
    # TOPIC-BASED SEARCHES - Infrastructure & Supply Chain
    # ---------------------------------------------------------
    ("critical infrastructure cyber when:24h", "Critical Infrastructure"),
    ("supply chain attack when:24h", "Supply Chain"),
    ("power grid cyber when:24h", "Energy Security"),

    # ---------------------------------------------------------
    # TOPIC-BASED SEARCHES - General Cyber
    # ---------------------------------------------------------
    ("cybersecurity when:24h", "Cybersecurity"),
    ("Hackers when:24h", "Hackers"),
    ("cyber attack when:24h", "Cyber Attacks"),

    # ---------------------------------------------------------
    # TOPIC-BASED SEARCHES - Emerging Tech
    # ---------------------------------------------------------
    ("AI security when:24h", "AI Security"),
    ("quantum computing cyber when:24h", "Quantum Threats"),
    ("blockchain security when:24h", "Blockchain Security"),

    # ---------------------------------------------------------
    # TOPIC-BASED SEARCHES - Geopolitical
    # ---------------------------------------------------------
    ("Taiwan cyber when:24h", "Taiwan Security"),
    ("Ukraine cyber when:24h", "Ukraine Conflict"),
    ("Israel cyber when:24h", "Middle East Cyber"),

    # ---------------------------------------------------------
    # TOPIC-BASED SEARCHES - Industry Sectors
    # ---------------------------------------------------------
    ("healthcare cyber when:24h", "Healthcare Security"),
    ("financial cyber when:24h", "Financial Security"),
    ("maritime cyber when:24h", "Maritime Security"),

    # ---------------------------------------------------------
    # TOPIC-BASED SEARCHES - Technology Targets
    # ---------------------------------------------------------
    ("Huawei security when:24h", "Tech Companies"),
    ("5G security when:24h", "5G Networks"),
    ("IoT security when:24h", "IoT Security"),
    ("Ivanti when:24h", "VPN Security"),
]


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
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
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
        print(f"\n=== Searching: {category} ===")

        encoded = urllib.parse.quote(query)
        url = f"https://news.google.com/search?q={encoded}&hl={self.lang}&gl={self.gl}&ceid={self.ceid}"

        try:
            req = urllib.request.Request(url, headers=self.headers)
            html = urllib.request.urlopen(req, timeout=30).read()
            soup = Soup(html, "html.parser")
            cards = self.select_cards(soup)

            out = []
            for c in cards[:12]:
                article = self.parse_article(c, category)
                if article:
                    print(f"  ✓ {article['title'][:60]}...")
                    out.append(article)

            print(f"  → {len(out)} articles found")
            return out

        except Exception as e:
            print(f"  ✗ Error: {e}")
            return []

    def run_all_searches(self, queries=None):
        """Run all searches from the query list"""
        if queries is None:
            queries = SEARCH_QUERIES

        print(f"Starting Google News scraper with {len(queries)} queries...")

        all_articles = []

        for query, search_name in queries:
            articles = self.search_single_query(query, search_name)
            all_articles.extend(articles)
            time.sleep(random.uniform(0.4, 1.0))

        unique_articles = self.remove_duplicates(all_articles)

        print(f"\n{'='*50}")
        print(f"RESULTS: {len(all_articles)} total → {len(unique_articles)} unique")
        print(f"{'='*50}")

        # Category breakdown
        categories = {}
        for article in unique_articles:
            cat = article.get('search_category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1

        print(f"\nBy category:")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:20]:
            print(f"  {cat}: {count}")

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
    """Main scraping function"""
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
    """Save news data to CSV and JSON files"""
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
    print("=" * 60)
    print("COMPREHENSIVE CYBER NEWS SCRAPER")
    print(f"Sources: {len(SEARCH_QUERIES)} queries")
    print("=" * 60)

    try:
        news = scrape_google_news_multi()

        if news:
            save_to_csv(news)
            print(f"\n✓ Successfully processed {len(news)} articles")

            print(f"\nSample articles:")
            for i, article in enumerate(news[:5]):
                print(f"  {i+1}. {article['Title'][:70]}...")
                print(f"     Source: {article['Source']} | Category: {article['Category']}")

        else:
            print("No articles found!")
            with open("data/latest_news.json", "w") as f:
                json.dump([], f)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        with open("data/latest_news.json", "w") as f:
            json.dump([], f)


if __name__ == "__main__":
    main()
