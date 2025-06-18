#!/usr/bin/env python3
"""
Publish Articles
Set article status to 'published' so they appear on homepage
"""

import os
import sys

# Add src to path  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.db_manager import DatabaseManager

def publish_all_articles():
    """Publish all draft articles"""
    
    db = DatabaseManager()
    
    # Check current article statuses
    articles = db.execute_query("SELECT id, title, status FROM articles")
    
    print("📋 Current Articles:")
    for article in articles:
        print(f"  ID {article['id']}: {article['title']} - Status: {article['status']}")
    
    # Update all articles to published status
    update_query = "UPDATE articles SET status = 'published' WHERE status != 'published'"
    result = db.execute_write(update_query)
    
    print(f"\n✅ Updated articles to published status")
    
    # Check updated statuses
    articles = db.execute_query("SELECT id, title, status FROM articles")
    
    print("\n📋 Updated Articles:")
    for article in articles:
        print(f"  ID {article['id']}: {article['title']} - Status: {article['status']}")
    
    return True

if __name__ == "__main__":
    print("📰 Publishing articles...")
    
    if publish_all_articles():
        print("\n✅ All articles published successfully!")
        print("\nRegenerate homepage with:")
        print("python3 scripts/generate_homepage_simple.py")
    else:
        print("\n❌ Failed to publish articles!")
        sys.exit(1)