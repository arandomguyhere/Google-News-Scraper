# Optimized search strategy based on successful 367-article results
# Key improvements: Better targeting, reduced redundancy, international sources

def get_optimized_searches():
    """
    Optimized search categories based on analysis of successful 367-article scrape.
    Total: ~40 targeted searches with better yield per search.
    """
    
    searches = [
        # ============================================================================
        # 1. NATION-STATE ACTORS (Consolidated for better targeting)
        # ============================================================================
        ("(China cyber OR Chinese hackers OR PLA cyber) when:24h", "China Cyber Operations"),
        ("(Russia cyber OR Russian hackers OR APT28 OR APT29) when:24h", "Russia Cyber Operations"), 
        ("(Iran cyber OR Iranian hackers OR Pay2Key) when:24h", "Iran Cyber Operations"),
        ("(North Korea cyber OR DPRK cyber OR Lazarus Group) when:24h", "North Korea Cyber Operations"),
        
        # ============================================================================
        # 2. HIGH-VOLUME ATTACK CATEGORIES (Your top performers)
        # ============================================================================
        ("ransomware attack when:24h", "Ransomware Attacks"),  # 7 articles - good yield
        ("zero day exploit OR 0-day when:24h", "Zero-Day Exploits"),  # 8 articles - excellent
        ("data breach OR cyber attack when:24h", "Cyber Attacks & Breaches"),  # Combine for 15+ articles
        ("malware OR trojan OR spyware when:24h", "Malware Threats"),  # 6 articles
        ("phishing OR social engineering when:24h", "Phishing & Social Engineering"),  # 19 articles combined
        
        # ============================================================================
        # 3. CRITICAL INFRASTRUCTURE (High-impact targets)
        # ============================================================================
        ("critical infrastructure cyber when:24h", "Critical Infrastructure"),
        ("healthcare cyber OR hospital hack when:24h", "Healthcare Security"),  # 9 articles - good
        ("financial cyber OR banking security when:24h", "Financial Security"),  # 9 articles - good
        ("energy cyber OR power grid hack when:24h", "Energy Security"),
        ("supply chain attack when:24h", "Supply Chain Security"),
        
        # ============================================================================
        # 4. EMERGING TECH THREATS (Growing importance)
        # ============================================================================
        ("AI security OR artificial intelligence hack when:24h", "AI Security"),  # 10 articles - excellent
        ("IoT security OR smart device hack when:24h", "IoT Security"),  # 9 articles - good
        ("5G security OR telecom hack when:24h", "5G & Telecom Security"),  # 8 articles
        ("blockchain security OR crypto hack when:24h", "Blockchain & Crypto Security"),  # 10 articles
        ("quantum threat OR post-quantum crypto when:24h", "Quantum Security"),
        
        # ============================================================================
        # 5. GEOPOLITICAL CYBER HOTSPOTS
        # ============================================================================
        ("Taiwan cyber OR Taiwan hack when:24h", "Taiwan Cyber Threats"),  # 10 articles - excellent
        ("Ukraine cyber OR Ukraine hack when:24h", "Ukraine Cyber Warfare"),
        ("Israel cyber OR Middle East hack when:24h", "Middle East Cyber"),
        
        # ============================================================================
        # 6. TECHNICAL VULNERABILITIES (High-value intelligence)
        # ============================================================================
        ("CVE OR vulnerability disclosure when:24h", "Security Vulnerabilities"),  # 9 articles
        ("Ivanti OR VPN vulnerability when:24h", "VPN & Remote Access Security"),  # 5 articles
        ("Microsoft patch OR Windows vulnerability when:24h", "Microsoft Security Updates"),
        ("APT group OR advanced persistent threat when:24h", "Advanced Threat Groups"),
        
        # ============================================================================
        # 7. PREMIUM WESTERN SOURCES (Better cyber-focused queries)
        # ============================================================================
        ("site:ft.com (cyber OR hack OR breach OR security) when:24h", "Financial Times Cyber"),
        ("site:wsj.com (cybersecurity OR hacker OR breach) when:24h", "Wall Street Journal Cyber"),
        ("site:reuters.com (cyber OR hack OR malware) when:24h", "Reuters Cyber Coverage"),
        ("site:bloomberg.com (cybersecurity OR hack OR breach) when:24h", "Bloomberg Cyber Coverage"),
        
        # ============================================================================
        # 8. SPECIALIZED SECURITY PUBLICATIONS (Your best sources)
        # ============================================================================
        ("site:krebsonsecurity.com when:24h", "Krebs on Security"),
        ("site:darkreading.com when:24h", "Dark Reading Analysis"),
        ("site:securityweek.com when:24h", "Security Week Reports"),
        ("site:theregister.com (security OR cyber OR hack) when:24h", "The Register Security"),
        ("site:bleepingcomputer.com when:24h", "BleepingComputer News"),
        ("site:thehackernews.com when:24h", "The Hacker News"),
        ("site:https://gbhackers.com/ when:24h", "GBhackers"),
        
        # ============================================================================
        # 9. INTERNATIONAL SOURCES (Based on regional research)
        # ============================================================================
        # China/Asia-Pacific
        ("site:scmp.com cyber when:24h", "South China Morning Post Cyber"),
        ("site:chinadaily.com.cn cyber when:24h", "China Daily Cyber"),
        ("site:globaltimes.cn cyber when:24h", "Global Times Cyber"),
        
        # Russia/Eastern Europe  
        ("site:rt.com cyber when:24h", "RT Cyber Coverage"),
        ("site:kommersant.ru cyber when:24h", "Kommersant Cyber"),
        
        # Iran/Middle East
        ("site:presstv.ir cyber when:24h", "Press TV Iran Cyber"),
        ("site:iranintl.com cyber when:24h", "Iran International Cyber"),
        ("site:irna.ir cyber when:24h", "IRNA Cyber Coverage"),
        
        # Africa
        ("site:dailymaverick.co.za cyber when:24h", "Daily Maverick Africa Cyber"),
        ("site:itweb.co.za cyber when:24h", "ITWeb Africa Cyber"),
        ("site:cybersecuritymag.africa when:24h", "Africa CyberSecurity Magazine"),
        
        # Latin America
        ("site:infobae.com ciberseguridad when:24h", "Infobae Latin America Cyber"),
        ("site:univision.com cyber when:24h", "Univision Cyber Coverage"),
        ("site:cybersecuritynews.es when:24h", "CyberSecurity News España"),
        
        # ============================================================================
        # 10. INDUSTRY-SPECIFIC SEARCHES (High-value sectors)
        # ============================================================================
        ("maritime cyber OR shipping hack when:24h", "Maritime Security"),  # 8 articles - good
        ("manufacturing cyber OR industrial hack when:24h", "Industrial Security"),
        ("government cyber OR state hack when:24h", "Government Security"),
        ("election security OR voting hack when:24h", "Election Security"),
    ]
    
    return searches

# Enhanced deduplication for better results
def enhanced_remove_duplicates(self, articles):
    """
    Enhanced deduplication with better similarity detection
    """
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
            
        # Check title similarity with multiple methods
        is_duplicate = False
        title_words = set(title.split())
        
        for seen_title in seen_titles:
            seen_words = set(seen_title.split())
            
            if len(title_words) > 0 and len(seen_words) > 0:
                # Method 1: Word overlap similarity
                word_similarity = len(title_words.intersection(seen_words)) / max(len(title_words), len(seen_words))
                
                # Method 2: Character-based similarity for similar headlines
                char_similarity = len(set(title).intersection(set(seen_title))) / max(len(title), len(seen_title))
                
                # Method 3: Check for news agency rewrites (common prefixes/suffixes)
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

# Performance optimization for high-volume scraping
def optimized_search_single_query(self, query, search_name, max_articles=10):
    """
    Optimized version with better error handling and performance
    """
    print(f"\n{'='*50}")
    print(f"Searching: {search_name}")
    print(f"Query: {query}")
    print(f"Target: {max_articles} articles")
    print(f"{'='*50}")
    
    # Build Google News search URL with better parameters
    encoded_query = urllib.parse.quote(query.encode('utf-8'))
    # Add more specific news parameters
    url = f'https://news.google.com/search?q={encoded_query}&hl={self.lang}&gl=US&ceid=US:en'
    
    try:
        # Adaptive delay based on previous success
        delay = random.uniform(2, 5) if hasattr(self, 'rate_limited') else random.uniform(1, 3)
        time.sleep(delay)
        
        req = urllib.request.Request(url, headers=self.headers)
        response = urllib.request.urlopen(req, timeout=45)  # Longer timeout
        page = response.read()
        content = Soup(page, "html.parser")
        
        # Enhanced article extraction with multiple fallback methods
        articles = content.select('article')
        if not articles:
            # Fallback: try different selectors
            articles = content.select('[role="article"]') or content.select('.xrnccd')
        
        print(f"Found {len(articles)} article elements")
        
        valid_articles = []
        
        for i, article in enumerate(articles):
            if len(valid_articles) >= max_articles:
                break
                
            try:
                # Enhanced title extraction with more methods
                title = self.extract_title_enhanced(article)
                if not title or len(title) < 15:
                    continue
                
                # Skip navigation and irrelevant items
                if self.is_navigation_item(title):
                    continue
                
                # Enhanced metadata extraction
                link = self.extract_link_enhanced(article, url)
                date, datetime_obj = self.extract_date_enhanced(article)
                media = self.extract_media_enhanced(article, search_name)
                img = self.extract_image_enhanced(article)
                
                # Quality scoring for better filtering
                quality_score = self.calculate_article_quality(title, media, link)
                if quality_score < 0.5:  # Skip low-quality articles
                    continue
                
                print(f"  ✓ Found: {title[:60]}... (Source: {media}) [Quality: {quality_score:.2f}]")
                
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
        return valid_articles
        
    except Exception as e:
        print(f"✗ {search_name}: Error during search: {e}")
        if "429" in str(e) or "rate" in str(e).lower():
            self.rate_limited = True
            print("  Rate limiting detected - increasing delays")
        return []

def calculate_article_quality(self, title, media, link):
    """
    Calculate article quality score based on multiple factors
    """
    score = 0.5  # Base score
    
    # Title quality
    if len(title) > 30:
        score += 0.1
    if any(word in title.lower() for word in ['cyber', 'hack', 'security', 'breach', 'malware']):
        score += 0.2
    
    # Source quality
    quality_sources = ['reuters', 'bloomberg', 'wsj', 'ft.com', 'krebsonsecurity', 
                      'darkreading', 'securityweek', 'bleepingcomputer']
    if any(source in media.lower() for source in quality_sources):
        score += 0.3
    
    # Link quality
    if link and 'news.google.com' not in link:
        score += 0.1
    
    return min(score, 1.0)  # Cap at 1.0
