# Add this to your scraper.py to track search query performance

import json
from datetime import datetime
from pathlib import Path

class SearchQueryTracker:
    def __init__(self):
        self.query_stats_file = Path("data/search_query_stats.json")
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        """Ensure tracking file exists"""
        if not self.query_stats_file.exists():
            self.query_stats_file.parent.mkdir(exist_ok=True)
            with open(self.query_stats_file, 'w') as f:
                json.dump({"queries": {}, "sessions": {}}, f)
    
    def track_query_performance(self, query, search_name, articles_found, timestamp=None):
        """Track the performance of individual search queries"""
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        with open(self.query_stats_file, 'r') as f:
            stats = json.load(f)
        
        query_key = f"{search_name}|||{query}"  # Use ||| as separator
        
        if query_key not in stats["queries"]:
            stats["queries"][query_key] = {
                "search_name": search_name,
                "query": query,
                "total_uses": 0,
                "total_articles": 0,
                "average_articles": 0,
                "success_rate": 0,  # % of times it found 6+ articles
                "best_session": {"count": 0, "timestamp": ""},
                "worst_session": {"count": float('inf'), "timestamp": ""},
                "first_used": timestamp,
                "last_used": timestamp,
                "hit_target_count": 0,  # Times it hit exactly 6
                "exceeded_target_count": 0,  # Times it found >6
                "failed_count": 0  # Times it found 0
            }
        
        query_data = stats["queries"][query_key]
        
        # Update statistics
        query_data["total_uses"] += 1
        query_data["total_articles"] += articles_found
        query_data["last_used"] = timestamp
        query_data["average_articles"] = query_data["total_articles"] / query_data["total_uses"]
        
        # Track target performance
        if articles_found == 6:
            query_data["hit_target_count"] += 1
        elif articles_found > 6:
            query_data["exceeded_target_count"] += 1
        elif articles_found == 0:
            query_data["failed_count"] += 1
        
        # Update success rate (6+ articles)
        success_sessions = query_data["hit_target_count"] + query_data["exceeded_target_count"]
        query_data["success_rate"] = (success_sessions / query_data["total_uses"]) * 100
        
        # Update best/worst sessions
        if articles_found > query_data["best_session"]["count"]:
            query_data["best_session"] = {"count": articles_found, "timestamp": timestamp}
        if articles_found < query_data["worst_session"]["count"]:
            query_data["worst_session"] = {"count": articles_found, "timestamp": timestamp}
        
        # Store session data
        if timestamp not in stats["sessions"]:
            stats["sessions"][timestamp] = {}
        stats["sessions"][timestamp][query_key] = {
            "articles_found": articles_found,
            "search_name": search_name,
            "query": query
        }
        
        with open(self.query_stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
    
    def generate_query_report(self):
        """Generate a detailed report of query performance"""
        with open(self.query_stats_file, 'r') as f:
            stats = json.load(f)
        
        print("\n" + "="*80)
        print("SEARCH QUERY PERFORMANCE REPORT")
        print("="*80)
        
        # Sort queries by success rate
        sorted_queries = sorted(
            stats["queries"].items(),
            key=lambda x: x[1]["success_rate"],
            reverse=True
        )
        
        print(f"\n🎯 TOP PERFORMING QUERIES (by success rate - 6+ articles)")
        print(f"{'='*80}")
        print(f"{'Rank':<4} | {'Category':<20} | {'Success %':<9} | {'Avg Arts':<8} | {'Total Uses':<10} | {'Query'}")
        print(f"{'-'*80}")
        
        for i, (query_key, data) in enumerate(sorted_queries[:20], 1):
            category = data["search_name"][:20]
            query_text = data["query"][:30] + "..." if len(data["query"]) > 30 else data["query"]
            print(f"{i:4d} | {category:<20} | {data['success_rate']:8.1f}% | {data['average_articles']:7.1f} | {data['total_uses']:10d} | {query_text}")
        
        print(f"\n❌ UNDERPERFORMING QUERIES (success rate < 50%)")
        print(f"{'='*80}")
        underperforming = [item for item in sorted_queries if item[1]["success_rate"] < 50]
        
        if underperforming:
            print(f"{'Category':<20} | {'Success %':<9} | {'Avg Arts':<8} | {'Failed':<7} | {'Query'}")
            print(f"{'-'*70}")
            for query_key, data in underperforming[:15]:
                category = data["search_name"][:20]
                query_text = data["query"][:40] + "..." if len(data["query"]) > 40 else data["query"]
                print(f"{category:<20} | {data['success_rate']:8.1f}% | {data['average_articles']:7.1f} | {data['failed_count']:7d} | {query_text}")
        else:
            print("🎉 All queries performing above 50% success rate!")
        
        print(f"\n📊 QUERY STATISTICS BY CATEGORY")
        print(f"{'='*80}")
        
        # Group by category
        category_stats = {}
        for query_key, data in stats["queries"].items():
            category = data["search_name"]
            if category not in category_stats:
                category_stats[category] = {
                    "total_queries": 0,
                    "total_uses": 0,
                    "total_articles": 0,
                    "successful_queries": 0,
                    "avg_success_rate": 0
                }
            
            cat_data = category_stats[category]
            cat_data["total_queries"] += 1
            cat_data["total_uses"] += data["total_uses"]
            cat_data["total_articles"] += data["total_articles"]
            if data["success_rate"] >= 50:
                cat_data["successful_queries"] += 1
        
        # Calculate averages
        for category, data in category_stats.items():
            if data["total_queries"] > 0:
                data["avg_success_rate"] = sum(
                    stats["queries"][q]["success_rate"] 
                    for q in stats["queries"] 
                    if stats["queries"][q]["search_name"] == category
                ) / data["total_queries"]
        
        sorted_categories = sorted(
            category_stats.items(),
            key=lambda x: x[1]["avg_success_rate"],
            reverse=True
        )
        
        print(f"{'Category':<25} | {'Queries':<7} | {'Avg Success %':<12} | {'Total Articles':<14} | {'Total Uses'}")
        print(f"{'-'*80}")
        for category, data in sorted_categories:
            print(f"{category:<25} | {data['total_queries']:7d} | {data['avg_success_rate']:11.1f}% | "
                  f"{data['total_articles']:14d} | {data['total_uses']:10d}")
        
        print(f"\n🔄 MOST FREQUENTLY USED QUERIES")
        print(f"{'='*80}")
        most_used = sorted(
            stats["queries"].items(),
            key=lambda x: x[1]["total_uses"],
            reverse=True
        )
        
        print(f"{'Uses':<5} | {'Category':<20} | {'Success %':<9} | {'Avg Arts':<8} | {'Query'}")
        print(f"{'-'*70}")
        for query_key, data in most_used[:15]:
            category = data["search_name"][:20]
            query_text = data["query"][:35] + "..." if len(data["query"]) > 35 else data["query"]
            print(f"{data['total_uses']:5d} | {category:<20} | {data['success_rate']:8.1f}% | "
                  f"{data['average_articles']:7.1f} | {query_text}")
        
        print(f"\n⭐ BEST INDIVIDUAL QUERY PERFORMANCES")
        print(f"{'='*80}")
        best_performers = sorted(
            stats["queries"].items(),
            key=lambda x: x[1]["best_session"]["count"],
            reverse=True
        )
        
        print(f"{'Max Arts':<8} | {'Category':<20} | {'Session':<15} | {'Query'}")
        print(f"{'-'*70}")
        for query_key, data in best_performers[:10]:
            if data["best_session"]["count"] > 0:
                category = data["search_name"][:20]
                session = data["best_session"]["timestamp"]
                query_text = data["query"][:30] + "..." if len(data["query"]) > 30 else data["query"]
                print(f"{data['best_session']['count']:8d} | {category:<20} | {session:<15} | {query_text}")
        
        # Query recommendations
        print(f"\n💡 QUERY OPTIMIZATION RECOMMENDATIONS")
        print(f"{'='*80}")
        
        # Find queries that consistently fail
        failing_queries = [
            (k, v) for k, v in stats["queries"].items() 
            if v["success_rate"] < 25 and v["total_uses"] >= 3
        ]
        
        if failing_queries:
            print("❌ Consider replacing these consistently failing queries:")
            for query_key, data in failing_queries[:5]:
                print(f"   • {data['search_name']}: '{data['query']}' (Success: {data['success_rate']:.1f}%)")
        
        # Find highly successful queries for expansion
        successful_queries = [
            (k, v) for k, v in stats["queries"].items() 
            if v["success_rate"] > 80 and v["total_uses"] >= 3
        ]
        
        if successful_queries:
            print("\n✅ Consider creating similar queries based on these high performers:")
            for query_key, data in successful_queries[:5]:
                print(f"   • {data['search_name']}: '{data['query']}' (Success: {data['success_rate']:.1f}%)")
        
        # Category gaps
        all_categories = set(data["search_name"] for data in stats["queries"].values())
        weak_categories = [
            cat for cat, data in category_stats.items() 
            if data["avg_success_rate"] < 60
        ]
        
        if weak_categories:
            print(f"\n⚠️  Categories needing more/better queries:")
            for category in weak_categories:
                avg_rate = category_stats[category]["avg_success_rate"]
                print(f"   • {category} (Avg Success: {avg_rate:.1f}%)")
        
        print(f"\n" + "="*80)
        print("Query Performance Report generated at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print("="*80)
    
    def get_query_suggestions(self, category):
        """Get suggestions for improving queries in a specific category"""
        with open(self.query_stats_file, 'r') as f:
            stats = json.load(f)
        
        category_queries = [
            (k, v) for k, v in stats["queries"].items() 
            if v["search_name"] == category
        ]
        
        if not category_queries:
            return f"No queries found for category: {category}"
        
        # Find best and worst performing queries in this category
        best_query = max(category_queries, key=lambda x: x[1]["success_rate"])
        worst_query = min(category_queries, key=lambda x: x[1]["success_rate"])
        
        suggestions = {
            "category": category,
            "total_queries": len(category_queries),
            "best_performer": {
                "query": best_query[1]["query"],
                "success_rate": best_query[1]["success_rate"],
                "average_articles": best_query[1]["average_articles"]
            },
            "worst_performer": {
                "query": worst_query[1]["query"],
                "success_rate": worst_query[1]["success_rate"],
                "average_articles": worst_query[1]["average_articles"]
            },
            "recommendations": []
        }
        
        # Generate recommendations based on performance
        avg_success = sum(q[1]["success_rate"] for q in category_queries) / len(category_queries)
        
        if avg_success < 50:
            suggestions["recommendations"].append(
                "Consider revising search terms - current queries have low success rate"
            )
        
        if best_query[1]["success_rate"] > 80:
            suggestions["recommendations"].append(
                f"Expand on successful pattern: '{best_query[1]['query']}'"
            )
        
        if worst_query[1]["success_rate"] < 25:
            suggestions["recommendations"].append(
                f"Replace or modify: '{worst_query[1]['query']}'"
            )
        
        return suggestions
    
    def export_query_performance(self):
        """Export query performance to CSV"""
        with open(self.query_stats_file, 'r') as f:
            stats = json.load(f)
        
        export_data = []
        for query_key, data in stats["queries"].items():
            export_data.append({
                "Search_Name": data["search_name"],
                "Query": data["query"],
                "Total_Uses": data["total_uses"],
                "Total_Articles": data["total_articles"],
                "Average_Articles": data["average_articles"],
                "Success_Rate_Percent": data["success_rate"],
                "Hit_Target_Count": data["hit_target_count"],
                "Exceeded_Target_Count": data["exceeded_target_count"],
                "Failed_Count": data["failed_count"],
                "Best_Session_Count": data["best_session"]["count"],
                "Worst_Session_Count": data["worst_session"]["count"],
                "First_Used": data["first_used"],
                "Last_Used": data["last_used"]
            })
        
        import pandas as pd
        df = pd.DataFrame(export_data)
        
        output_dir = Path("data/exports")
        output_dir.mkdir(exist_ok=True)
        
        df.to_csv(output_dir / "query_performance.csv", index=False)
        print(f"✅ Query performance exported to {output_dir}/query_performance.csv")
        
        return output_dir / "query_performance.csv"

# Integration code to add to your main scraper.py

# Add this to the top of your scraper.py:
query_tracker = SearchQueryTracker()

# Modify your search_single_query method to include tracking:
def search_single_query(self, query, search_name):
    """Search Google News for a single query - Enhanced with performance tracking"""
    print(f"\n{'='*50}")
    print(f"Searching: {search_name}")
    print(f"Query: {query}")
    print(f"Target: 6 articles per category")
    print(f"{'='*50}")
    
    # ... your existing search code ...
    
    # At the end of the method, add tracking:
    articles_found = len(valid_articles)
    
    # Track query performance
    global query_tracker
    query_tracker.track_query_performance(query, search_name, articles_found)
    
    print(f"✓ {search_name}: Found {articles_found}/6 target articles")
    if articles_found < 6:
        print(f"  ⚠️  Warning: Only found {articles_found} articles (target was 6)")
    
    return valid_articles

# Add this function to generate reports after scraping:
def generate_all_reports():
    """Generate comprehensive reports including query performance"""
    print("\n🔍 GENERATING QUERY PERFORMANCE REPORT")
    query_tracker.generate_query_report()
    
    print("\n📊 EXPORTING QUERY PERFORMANCE DATA")
    query_tracker.export_query_performance()

# Add to your main() function:
def main():
    """Main function with enhanced reporting"""
    try:
        print("Starting Comprehensive Multi-Search Google News scraper...")
        
        # Your existing scraper code...
        news = scrape_google_news_multi()
        
        if news:
            save_to_csv(news)
            print(f"\nSuccessfully processed {len(news)} articles")
            
            # Generate comprehensive reports
            generate_all_reports()
            
        else:
            print("No articles found!")
            
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
