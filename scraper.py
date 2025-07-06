def run_all_searches(self):
    """Run all the individual searches"""
    print("Starting multi-search Google News scraping...")
    print("Searches: China Cyber, Russian Cyber, General Cyber, Iran Cyber")
    
    # Define all searches with expanded keywords from Bob's analysis
    searches = [
        # Core cyber operations
        ("China cyber when:24h", "China Cyber"),
        ("Russian cyber when:24h", "Russian Cyber"), 
        ("Iran cyber when:24h", "Iran Cyber"),
        ("cybersecurity when:24h", "Cybersecurity"),
        ("cyber attack when:24h", "Cyber Attacks"),
        
        # APT Groups and Threat Actors
        ("APT when:24h", "APT Groups"),
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
        
        # Site-specific searches - General tech/security coverage
        ("site:ft.com when:24h", "Financial Times"),
        ("site:theregister.com when:24h", "The Register"),
        ("site:forbes.com when:24h", "Forbes"),
        ("site:wsj.com when:24h", "Wall Street Journal"),
        
        # Site-specific searches - Cyber-focused
        ("site:ft.com cyber when:24h", "FT Cyber"),
        ("site:theregister.com security when:24h", "Register Security"),
        ("site:forbes.com cybersecurity when:24h", "Forbes Cyber"),
        ("site:wsj.com cyber when:24h", "WSJ Cyber"),
        
        # Additional premium sources
        ("site:reuters.com cyber when:24h", "Reuters Cyber"),
        ("site:bloomberg.com cybersecurity when:24h", "Bloomberg Cyber"),
        ("site:techcrunch.com security when:24h", "TechCrunch Security"),
        ("site:wired.com cyber when:24h", "Wired Cyber"),
        
        # Specialized security publications
        ("site:krebsonsecurity.com when:24h", "Krebs Security"),
        ("site:darkreading.com when:24h", "Dark Reading"),
        ("site:securityweek.com when:24h", "Security Week"),
    ]
    
    all_articles = []
    
    for query, search_name in searches:
        articles = self.search_single_query(query, search_name)
        all_articles.extend(articles)
        
        # Add delay between searches
        time.sleep(random.uniform(1, 3))
    
    # Remove duplicates based on title similarity
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
    for cat, count in categories.items():
        print(f"  {cat}: {count} articles")
    
    self.all_results = unique_articles
    return unique_articles
