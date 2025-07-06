#!/usr/bin/env python3
"""
Archive Manager for Bob's Brief - Cyber Intelligence Collection
Creates timestamped archives of each scraping session
"""

import json
import os
import shutil
from datetime import datetime
import pandas as pd
from pathlib import Path

def create_timestamped_archive():
    """Create a timestamped archive of the current scraping session"""
    
    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create archive directory structure
    archive_base = Path("archives")
    archive_dir = archive_base / timestamp
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating archive: {timestamp}")
    
    # Archive the JSON data
    json_source = Path("data/latest_news.json")
    json_archive = archive_dir / f"news_{timestamp}.json"
    
    if json_source.exists():
        shutil.copy2(json_source, json_archive)
        print(f"✓ Archived JSON: {json_archive}")
        
        # Load data for statistics
        with open(json_source, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
    else:
        # Create empty archive if no data
        with open(json_archive, 'w', encoding='utf-8') as f:
            json.dump([], f)
        news_data = []
        print("⚠️ No JSON data found, created empty archive")
    
    # Archive the CSV data
    csv_source = Path("data/latest_news.csv")
    csv_archive = archive_dir / f"news_{timestamp}.csv"
    
    if csv_source.exists():
        shutil.copy2(csv_source, csv_archive)
        print(f"✓ Archived CSV: {csv_archive}")
    else:
        # Create empty CSV if no data
        df = pd.DataFrame(columns=['Title', 'Link', 'Source', 'Published', 'Category', 'img', 'Scraped_At'])
        df.to_csv(csv_archive, index=False)
        print("⚠️ No CSV data found, created empty archive")
    
    # Create metadata
    metadata = {
        "timestamp": timestamp,
        "created_at": datetime.now().isoformat(),
        "total_articles": len(news_data),
        "archive_path": str(archive_dir)
    }
    
    # Save metadata
    metadata_file = archive_dir / "metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Created metadata: {metadata_file}")
    
    # Update archive index
    index_file = Path("archives/archive_index.txt")
    with open(index_file, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp}\n")
    
    print(f"✅ Archive {timestamp} created successfully")
    print(f"   Path: {archive_dir}")
    print(f"   Articles: {len(news_data)}")
    
    return {
        "timestamp": timestamp,
        "path": str(archive_dir),
        "articles": len(news_data)
    }

def main():
    """Main function for archive management"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            result = create_timestamped_archive()
            print(f"Archive created: {result}")
        else:
            print("Usage: python archive_manager.py [create]")
    else:
        # Default: create archive
        result = create_timestamped_archive()
        print(f"Archive created: {result}")

if __name__ == "__main__":
    main()
