import urllib.request
import urllib.parse
from bs4 import BeautifulSoup as Soup
import pandas as pd
import os
import time
from datetime import datetime, timedelta
import json
import re
import random

# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs("docs", exist_ok=True)

def define_date(date):
    """Convert relative date strings to datetime objects"""
    if not date:
        return None
    
    try:
        if ' ago' in date.lower():
            parts = date.split()
            if len(parts) >= 3:
                q = int(parts[0])
                if 'minute' in date.lower():
                    return datetime.now() - timedelta(minutes=q)
                elif 'hour' in date.lower():
                    return datetime.now() - timedelta(hours=q)
                elif 'day' in date.lower():
                    return datetime.now() - timedelta(days=q)
                elif 'week' in date.lower():
                    return datetime.now() - timedelta(days=7*q)
        elif 'yesterday' in date.lower():
            return datetime.now() - timedelta(days=1)
        else:
            return datetime.now()
    except:
        return datetime.now()

def process_image_url(img_src):
    """Process and validate image URL from Google News"""
    if not img_src:
        return None
    
    # Handle different URL formats from Google News
    if img_src.startswith('//'):
        return 'https:' + img_src
    elif img_src.startswith('/'):
        return 'https://news.google.com' + img_src
    elif img_src.startswith('data:'):
        # Skip data URLs as they're usually tiny placeholders
        return None
    elif img_src.startswith('http'):
        # Already a full URL
        return img_src
    else:
        # Relative URL, make it absolute
        return 'https://news.google.com/' + img_src.lstrip('/')

class OptimizedMultiSearchGoogleNews:
    def __init__(self, lang="en", max_articles_per_search=10):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.lang = lang
        self.headers = {'User-Agent': self.user_agent}
        self.all_results = []
        self.max_articles = max_articles_per_search
        self.rate_limited = False
        self.performance_data = {}

    def extract_title_enhanced(self, article):
        """Enhanced title extraction with multiple fallback methods"""
        title = None
        
        # Method 1: Standard Google News structure
        try:
            divs = article.find_all('div')
            if len(divs) > 2:
                links = divs[2].find_all('a')
                if links:
                    title = links[0].get_text(strip=True)
        except:
            pass
        
        # Method 2: Alternative link structure
        if not title:
            try:
                links = article.find_all('a')
                if len(links) > 1:
                    title = links[1].get_text(strip=True)
            except:
                pass
        
        # Method 3: Header tags
        if not title:
            try:
                h_tag = article.find(['h3', 'h4', 'h2'])
                if h_tag:
                    title = h_tag.get_text(strip=True)
            except:
                pass
        
        # Method 4: First available link text
        if not title:
            try:
                link = article.find('a')
                if link:
                    title = link.get_text(strip=True)
            except:
                pass
        
        return title

    def extract_link_enhanced(self, article, fallback_url):
        """Enhanced link extraction"""
        link = None
        
        try:
            link_elem = article.find('div').find("a")
            if link_elem and link_elem.get("href"):
                href = link_elem.get("href")
                if href.startswith('./'):
                    link = 'https://news.google.com' + href[1:]
                elif href.startswith('/'):
                    link = 'https://news.google.com' + href
                else:
                    link = href
        except:
            try:
                # Alternative: first link in article
                link_elem = article.find('a')
                if link_elem and link_elem.get("href"):
                    href = link_elem.get("href")
                    if href.startswith('./'):
                        link = 'https://news.google.com' + href[1:]
                    elif href.startswith('/'):
                        link = 'https://news.google.com' + href
                    else:
                        link = href
            except:
                link = fallback_url
        
        return link

    def extract_date_enhanced(self, article):
        """Enhanced date extraction"""
        date = None
        datetime_obj = None
        
        try:
            time_elem = article.find("time")
            if time_elem:
                # Try datetime attribute first
                if time_elem.get("datetime"):
                    date = time_elem.get("datetime")
                else:
                    date = time_elem.get_text(strip=True)
                datetime_obj = define_date(date)
        except:
            date = "Recent"
            datetime_obj = datetime.now()
        
        return date, datetime_obj

    def extract_media_enhanced(self, article, search_name):
        """Enhanced media/source extraction"""
        media = None
        
        try:
            # Method 1: Near time element
            time_elem = article.find("time")
            if time_elem and time_elem.parent:
                source_link = time_elem.parent.find("a")
                if source_link:
                    media = source_link.get_text(strip=True)
        except:
            pass
        
        if not media:
            try:
                # Method 2: Deep dive into nested divs
                divs = article.find("div").find_all("div")
                if len(divs) > 1:
                    nested = divs[1].find("div")
                    if nested:
                        deeper = nested.find("div")
                        if deeper:
                            final = deeper.find("div")
                            if final:
                                media = final.get_text(strip=True)
            except:
                pass
        
        if not media:
            try:
                # Method 3: Look for source indicators
                source_candidates = article.find_all(['span', 'div'], string=re.compile(r'.*\.(com|org|net).*'))
                if source_candidates:
                    media = source_candidates[0].get_text(strip=True)
            except:
                pass
        
        # Validation and cleanup
        if not media or media == "" or len(media) > 50:
            media = f"{search_name} News"
        
        return media

    def extract_image_enhanced(self, article):
        """Enhanced image extraction with multiple methods"""
        img = None
        
        try:
            # Method 1: Figure/img tags
            img_elem = article.find("figure")
            if img_elem:
                img_tag = img_elem.find("img")
                if img_tag and img_tag.get("src"):
                    img_src = img_tag.get("src")
                    img = process_image_url(img_src)
            
            # Method 2: Direct img tag
            if not img:
                img_tag = article.find("img")
                if img_tag and img_tag.get("src"):
                    img_src = img_tag.get("src")
                    img = process_image_url(img_src)
            
            # Method 3: Img with classes
            if not img:
                img_candidates = article.find_all("img", class_=True)
                for img_candidate in img_candidates:
                    if img_candidate.get("src"):
                        img_src = img_candidate.get("src")
                        img = process_image_url(img_src)
                        if img:
                            break
            
            # Method 4: Lazy loading attributes
            if not img:
                img_tag = article.find("img", attrs={"data-src": True})
                if img_tag and img_tag.get("data-src"):
                    img_src = img_tag.get("data-src")
                    img = process_image_url(img_src)
        
        except Exception as e:
            print(f"    Error extracting image: {e}")
            img = None
        
        return img

    def is_navigation_item(self, title):
        """Check if title is a navigation item to skip"""
        title_lower = title.lower()
        nav_terms = ['home', 'for you', 'following', 'u.s.', 'world', 'local', 
                    'business', 'technology', 'entertainment', 'sports', 
                    'science', 'health', 'google news', 'more', 'sign in',
                    'search', 'menu', 'subscribe', 'newsletter']
        
        return any(nav_term == title_lower.strip() for nav_term in nav_terms)

    def calculate_article_quality(self, title, media, link):
        """Calculate article quality score"""
        score = 0.5  # Base score
        
        # Title quality
        if len(title) > 30:
            score += 0.1
        if any(word in title.lower() for word in ['cyber', 'hack', 'security', 'breach', 'malware', 'attack']):
            score += 0.2
        
        # Source quality
        quality_sources = ['reuters', 'bloomberg', 'wsj', 'ft.com', 'krebsonsecurity', 
                          'darkreading', 'securityweek', 'bleepingcomputer', 'thehackernews']
        if any(source in media.lower() for source in quality_sources):
            score += 0.3
        
        # Link quality
        if link and 'news.google.com' not in link:
            score += 0.1
        
        return min(score, 1.0)

    def search_single_query(self, query, search_name):
        """Search Google News for a single query - Enhanced version"""
        print(f"\n{'='*50}")
        print(f"Searching: {search_name}")
        print(f"Query: {query}")
        print(f"Target: {self.max_articles} articles")
        print(f"{'='*50}")
        
        # Build Google News search URL with enhanced parameters
        encoded_query = urllib.parse.quote(query.encode('utf-8'))
        url = f'https://news.google.com/search?q={encoded_query}&hl={self.lang}&gl=US&ceid=US:en'
        
        print(f"URL: {url}")
        
        try:
            # Adaptive delay based on rate limiting
            delay = random.uniform(3, 6) if self.rate_limited else random.uniform(2, 4)
            if 'site:' in query:
                delay = random.uniform(2, 5)  # Longer for site-specific queries
            time.sleep(delay)
            
            # Make request
            req = urllib.request.Request(url, headers=self.headers)
            response = urllib.request.urlopen(req, timeout=45)
            page = response.read()
            content = Soup(page, "html.parser")
            
            # Save debug HTML for first search
            if search_name == "China Cyber Operations":
                with open("debug_optimized_search.html", "w", encoding="utf-8") as f:
                    f.write(str(content))
                print("Saved debug HTML file")
            
            # Enhanced article finding
            articles = content.select('article')
            if not articles:
                # Fallback selectors
                articles = content.select('[role="article"]') or content.select('.xrnccd')
            
            print(f"Found {len(articles)} article elements")
            
            valid_articles = []
            
            for i, article in enumerate(articles):
                if len(valid_articles) >= self.max_articles:
                    break
                    
                try:
                    # Enhanced title extraction
                    title = self.extract_title_enhanced(article)
                    if not title or len(title) < 15:
                        continue
                    
                    # Skip navigation items
                    if self.is_navigation_item(title):
                        print(f"  ✗ Skipping navigation: {title}")
                        continue
                    
                    # Enhanced data extraction
                    link = self.extract_link_enhanced(article, url)
                    date, datetime_obj = self.extract_date_enhanced(article)
                    media = self.extract_media_enhanced(article, search_name)
                    img = self.extract_image_enhanced(article)
                    
                    # Quality scoring
                    quality_score = self.calculate_article_quality(title, media, link)
                    if quality_score < 0.5:  # Skip low-quality articles
                        continue
                    
                    print(f"  ✓ Found: {title[:60]}... (Source: {media}) [Quality: {quality_score:.2f}] {f'[IMG: {img[:30]}...]' if img else '[NO IMG]'}")
                    
                    valid_articles.append({
                        'title': title,
                        'desc': None,
                        'date': date,
                        'datetime': datetime_obj,
                        'link': link,
                        'img': img,
                        'media': media,
                        'site': media,
                        'reporter': None,
                        'search_category': search_name,
                        'quality_score': quality_score
                    })
                    
                except Exception as e:
                    print(f"  Error processing article {i+1}: {e}")
                    continue
            
            response.close()
            
            print(f"✓ {search_name}: Found {len(valid_articles)} quality articles")
            
            # Track performance
            self.performance_data[search_name] = len(valid_articles)
            
            return valid_articles
            
        except Exception as e:
            print(f"✗ {search_name}: Error during search: {e}")
            if "429" in str(e) or "rate" in str(e).lower():
                self.rate_limited = True
                print("  Rate limiting detected - increasing delays")
            return []

    def run_all_searches(self):
        """Run all optimized searches"""
        print("Starting OPTIMIZED multi-search Google News scraping...")
        print("Searches: 48 optimized categories covering Nation-state actors, APTs, Critical Infrastructure,")
        print("Zero-days, AI Security, Geopolitical Cyber, Attack Methods, Industry Sectors,")
        print("Premium News Sources + International Coverage")
        print("Timeframe: Last 24 hours for each search")
        
        # OPTIMIZED SEARCH CATEGORIES - Based on 367-article success + international sources
        searches = [
            # ============================================================================
            # 1. NATION-STATE THREAT ACTORS (Consolidated for better targeting)
            # ============================================================================
            ("(China cyber OR Chinese hackers OR PLA cyber) when:24h", "China Cyber Operations"),
            ("(Russia cyber OR Russian hackers OR APT28 OR APT29) when:24h", "Russia Cyber Operations"), 
            ("(Iran cyber OR Iranian hackers OR Pay2Key) when:24h", "Iran Cyber Operations"),
            ("(North Korea cyber OR DPRK cyber OR Lazarus Group) when:24h", "North Korea Cyber Operations"),
            
            # ============================================================================
            # 2. HIGH-YIELD ATTACK CATEGORIES (Proven performers)
            # ============================================================================
            ("ransomware attack when:24h", "Ransomware Attacks"),
            ("zero day exploit OR 0-day when:24h", "Zero-Day Exploits"),
            ("data breach OR cyber attack when:24h", "Cyber Attacks & Breaches"),
            ("malware OR trojan OR spyware when:24h", "Malware Threats"),
            ("phishing OR social engineering when:24h", "Phishing & Social Engineering"),
            
            # ============================================================================
            # 3. ADVANCED PERSISTENT THREAT GROUPS
            # ============================================================================
            ("APT29 OR Cozy Bear OR SVR when:24h", "Russian APT Groups"),
            ("APT28 OR Fancy Bear OR GRU when:24h", "Russian Military APTs"),
            ("APT1 OR Comment Crew OR PLA when:24h", "Chinese APT Groups"),
            ("Lazarus Group OR APT38 when:24h", "North Korean APTs"),
            ("advanced persistent threat OR state-sponsored hackers when:24h", "APT General"),
            
            # ============================================================================
            # 4. CRITICAL INFRASTRUCTURE
            # ============================================================================
            ("critical infrastructure cyber when:24h", "Critical Infrastructure"),
            ("healthcare cyber OR hospital hack when:24h", "Healthcare Security"),
            ("financial cyber OR banking security when:24h", "Financial Security"),
            ("energy cyber OR power grid hack when:24h", "Energy Security"),
            ("supply chain attack when:24h", "Supply Chain Security"),
            
            # ============================================================================
            # 5. EMERGING TECH THREATS (Top performers)
            # ============================================================================
            ("AI security OR artificial intelligence hack when:24h", "AI Security"),
            ("IoT security OR smart device hack when:24h", "IoT Security"),
            ("5G security OR telecom hack when:24h", "5G & Telecom Security"),
            ("blockchain security OR crypto hack when:24h", "Blockchain & Crypto Security"),
            ("quantum threat OR post-quantum crypto when:24h", "Quantum Security"),
            
            # ============================================================================
            # 6. GEOPOLITICAL CYBER HOTSPOTS
            # ============================================================================
            ("Taiwan cyber OR Taiwan hack when:24h", "Taiwan Cyber Threats"),
            ("Ukraine cyber OR Ukraine hack when:24h", "Ukraine Cyber Warfare"),
            ("Israel cyber OR Middle East hack when:24h", "Middle East Cyber"),
            
            # ============================================================================
            # 7. VULNERABILITIES & EXPLOITS
            # ============================================================================
            ("CVE OR vulnerability disclosure when:24h", "Security Vulnerabilities"),
            ("Ivanti OR VPN vulnerability when:24h", "VPN & Remote Access Security"),
            ("Microsoft patch OR Windows vulnerability when:24h", "Microsoft Security Updates"),
            
            # ============================================================================
            # 8. PREMIUM WESTERN SOURCES
            # ============================================================================
            ("site:ft.com (cyber OR hack OR breach OR security) when:24h", "Financial Times Cyber"),
            ("site:wsj.com (cybersecurity OR hacker OR breach) when:24h", "Wall Street Journal Cyber"),
            ("site:reuters.com (cyber OR hack OR malware) when:24h", "Reuters Cyber Coverage"),
            ("site:bloomberg.com (cybersecurity OR hack OR breach) when:24h", "Bloomberg Cyber Coverage"),
            
            # ============================================================================
            # 9. SPECIALIZED SECURITY PUBLICATIONS
            # ============================================================================
            ("site:krebsonsecurity.com when:24h", "Krebs on Security"),
            ("site:darkreading.com when:24h", "Dark Reading Analysis"),
            ("site:securityweek.com when:24h", "Security Week Reports"),
            ("site:theregister.com (security OR cyber OR hack) when:24h", "The Register Security"),
            ("site:bleepingcomputer.com when:24h", "BleepingComputer News"),
            ("site:thehackernews.com when:24h", "The Hacker News"),
            
            # ============================================================================
            # 10. INTERNATIONAL SOURCES (Global perspective)
            # ============================================================================
            # China/Asia-Pacific
            ("site:scmp.com cyber when:24h", "South China Morning Post Cyber"),
            ("site:chinadaily.com.cn cyber when:24h", "China Daily Cyber"),
            ("site:globaltimes.cn cyber when:24h", "Global Times Cyber"),
            
            # Russia/Eastern Europe  
            ("site:rt.com cyber when:24h", "RT Cyber Coverage"),
            
            # Iran/Middle East
            ("site:presstv.ir cyber when:24h", "Press TV Iran Cyber"),
            ("site:iranintl.com cyber when:24h", "Iran International Cyber"),
            ("site:irna.ir cyber when:24h", "IRNA Cyber Coverage"),
            
            # Africa
            ("site:dailymaverick.co.za cyber when:24h", "Daily Maverick Africa Cyber"),
            ("site:itweb.co.za cyber when:24h", "ITWeb Africa Cyber"),
            
            # Latin America
            ("site:infobae.com ciberseguridad when:24h", "Infobae Latin America Cyber"),
            ("site:univision.com cyber when:24h", "Univision Cyber Coverage"),
            
            # ============================================================================
            # 11. INDUSTRY-SPECIFIC SEARCHES
            # ============================================================================
            ("maritime cyber OR shipping hack when:24h", "Maritime Security"),
            ("manufacturing cyber OR industrial hack when:24h", "Industrial Security"),
            ("government cyber OR state hack when:24h", "Government Security"),
            ("election security OR voting hack when:24h", "Election Security"),
        ]
        
        all_articles = []
        
        print(f"\nStarting {len(searches)} searches...")
        
        for i, (query, search_name) in enumerate(searches, 1):
            print(f"\n[{i}/{len(searches)}] Processing: {search_name}")
            articles = self.search_single_query(query, search_name)
            all_articles.extend(articles)
            
            # Adaptive delays
            if i % 10 == 0:
                print(f"  Taking extended break after {i} searches...")
                time.sleep(random.uniform(10, 15))
        
        # Enhanced deduplication
        unique_articles = self.enhanced_remove_duplicates(all_articles)
        
        print(f"\n{'='*60}")
        print(f"OPTIMIZED SEARCH RESULTS")
        print(f"{'='*60}")
        print(f"Total searches conducted: {len(searches)}")
        print(f"Total articles found: {len(all_articles)}")
        print(f"Unique articles after deduplication: {len(unique_articles)}")
        
        # Performance analysis
        self.show_performance_analysis()
        self.show_enhanced_breakdown(unique_articles)
        
        self.all_results = unique_articles
        return unique_articles

    def enhanced_remove_duplicates(self, articles):
        """Enhanced deduplication with multiple similarity methods"""
        if not articles:
            return []
        
        unique_articles = []
        seen_titles = set()
        seen_links = set()
        
        for article in articles:
            title = article['title'].lower().strip()
            link = article.get('link', '').lower().strip()
            
            # Skip if exact link already seen
            if link and link in seen_links:
                continue
                
            # Enhanced similarity checking
            is_duplicate = False
            title_words = set(title.split())
            
            for seen_title in seen_titles:
                seen_words = set(seen_title.split())
                
                if len(title_words) > 0 and len(seen_words) > 0:
                    # Method 1: Word overlap similarity
                    word_similarity = len(title_words.intersection(seen_words)) / max(len(title_words), len(seen_words))
                    
                    # Method 2: Character-based similarity
                    char_similarity = len(set(title).intersection(set(seen_title))) / max(len(title), len(seen_title))
                    
                    # Method 3: Core content similarity (remove common prefixes)
                    title_core = title.replace('exclusive:', '').replace('breaking:', '').strip()
                    seen_core = seen_title.replace('exclusive:', '').replace('breaking:', '').strip()
                    core_similarity = len(set(title_core.split()).intersection(set(seen_core.split()))) / max(len(title_core.split()), len(seen_core.split()))
                    
                    if word_similarity > 0.75 or char_similarity > 0.85 or core_similarity > 0.8:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                seen_titles.add(title)
                if link:
                    seen_links.add(link)
                unique_articles.append(article)
        
        return unique_articles

    def show_performance_analysis(self):
        """Show search performance analysis"""
        if not self.performance_data:
            return
        
        # Sort by performance
        sorted_performance = sorted(self.performance_data.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n📊 SEARCH PERFORMANCE ANALYSIS:")
        print(f"{'Category':<35} {'Articles':<10} {'Performance'}")
        print(f"{'-'*60}")
        
        for category, count in sorted_performance:
            if count >= 8:
                status = "🔥 Excellent"
            elif count >= 5:
                status = "✅ Good"
            elif count >= 2:
                status = "⚠️  Fair"
            else:
                status = "❌ Poor"
            
            print(f"{category:<35} {count:<10} {status}")

    def show_enhanced_breakdown(self, articles):
        """Show results organized by logical groups"""
        groups = {
            'Nation-State Operations': ['China Cyber', 'Russia Cyber', 'Iran Cyber', 'North Korea Cyber'],
