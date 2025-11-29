#!/usr/bin/env python3
"""
Export arXiv database to JSON for GitHub Pages
By Yassine Ait Mohamed
"""

import sqlite3
import json
import sys
from pathlib import Path

def export_to_json(db_path="arxiv_collection.db", output_path="articles.json"):
    """
    Export SQLite database to JSON format for web display
    """
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM articles")
        total = cursor.fetchone()[0]
        print(f"📊 Found {total:,} articles in database")
        
        # Fetch all articles
        print("📥 Exporting articles...")
        cursor.execute("""
            SELECT arxiv_id, title, authors, abstract, category, published, link, pdf_link
            FROM articles 
            ORDER BY published DESC
        """)
        
        articles = []
        for row in cursor.fetchall():
            articles.append({
                'id': row[0],
                'title': row[1],
                'authors': row[2] if row[2] else 'Unknown',
                'abstract': row[3] if row[3] else '',
                'category': row[4],
                'published': row[5][:10] if row[5] else None,
                'link': row[6],
                'pdf': row[7]
            })
        
        conn.close()
        
        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Successfully exported {len(articles):,} articles to {output_path}")
        print(f"📦 File size: {Path(output_path).stat().st_size / 1024 / 1024:.2f} MB")
        
        # Show some stats
        categories = {}
        years = {}
        for article in articles:
            cat = article['category']
            categories[cat] = categories.get(cat, 0) + 1
            
            if article['published']:
                year = article['published'][:4]
                years[year] = years.get(year, 0) + 1
        
        print(f"\n📂 Categories: {len(categories)}")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"   {cat}: {count:,}")
        
        print(f"\n📅 Year range: {min(years.keys())} - {max(years.keys())}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Get database path from command line or use default
    db_path = sys.argv[1] if len(sys.argv) > 1 else "arxiv_collection.db"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "articles.json"
    
    print("="*80)
    print("🔄 arXiv Database to JSON Exporter")
    print("="*80 + "\n")
    
    if not Path(db_path).exists():
        print(f"❌ Database file not found: {db_path}")
        print("\nUsage: python export_to_json.py [db_path] [output_path]")
        sys.exit(1)
    
    success = export_to_json(db_path, output_path)
    
    if success:
        print("\n" + "="*80)
        print("✅ Export completed successfully!")
        print("="*80)
        print("\nNext steps:")
        print("1. Copy articles.json to your GitHub Pages repository")
        print("2. The website will automatically load and display your articles")
        print("3. Push to GitHub and your site will be live!")
    else:
        print("\n❌ Export failed")
        sys.exit(1)
