#!/usr/bin/env python3
"""
Database Schema Migration Script
===============================
Safely migrates from current schema.sql to the comprehensive schema matching documentation
"""

import sys
import sqlite3
import shutil
import os
from pathlib import Path
from datetime import datetime

# Add parent directories to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class SchemaMigrator:
    def __init__(self, db_path="data/infnews.db"):
        self.db_path = Path(db_path)
        self.backup_path = Path(f"data/infnews_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        self.new_schema_path = Path("src/database/schema_new.sql")
        
    def backup_database(self):
        """Create backup of current database"""
        print(f"📦 Creating backup: {self.backup_path}")
        
        if not self.db_path.exists():
            print(f"⚠️  Database {self.db_path} doesn't exist, creating new one")
            return
            
        shutil.copy2(self.db_path, self.backup_path)
        print(f"✅ Backup created successfully")
        
    def extract_existing_data(self):
        """Extract existing data from current database"""
        if not self.db_path.exists():
            print("No existing database found, will create new one")
            return {}
            
        print("📊 Extracting existing data...")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        data = {}
        
        try:
            # Extract authors
            cursor = conn.execute("SELECT * FROM authors")
            data['authors'] = [dict(row) for row in cursor.fetchall()]
            print(f"   📝 Found {len(data['authors'])} authors")
            
            # Extract categories  
            cursor = conn.execute("SELECT * FROM categories")
            data['categories'] = [dict(row) for row in cursor.fetchall()]
            print(f"   📂 Found {len(data['categories'])} categories")
            
            # Extract articles
            cursor = conn.execute("SELECT * FROM articles")
            data['articles'] = [dict(row) for row in cursor.fetchall()]
            print(f"   📄 Found {len(data['articles'])} articles")
            
            # Extract trending topics
            cursor = conn.execute("SELECT * FROM trending_topics")
            data['trending'] = [dict(row) for row in cursor.fetchall()]
            print(f"   📈 Found {len(data['trending'])} trending topics")
            
            # Extract images
            cursor = conn.execute("SELECT * FROM images")
            data['images'] = [dict(row) for row in cursor.fetchall()]
            print(f"   🖼️  Found {len(data['images'])} images")
            
            # Extract article sections
            cursor = conn.execute("SELECT * FROM article_sections")
            data['sections'] = [dict(row) for row in cursor.fetchall()]
            print(f"   📋 Found {len(data['sections'])} article sections")
            
            # Extract related articles
            cursor = conn.execute("SELECT * FROM related_articles") 
            data['related'] = [dict(row) for row in cursor.fetchall()]
            print(f"   🔗 Found {len(data['related'])} related article relationships")
            
        except sqlite3.OperationalError as e:
            print(f"⚠️  Error extracting data: {e}")
            print("   Some tables may not exist in current schema")
            
        finally:
            conn.close()
            
        return data
        
    def create_new_database(self):
        """Create new database with upgraded schema"""
        print("🚀 Creating new database with upgraded schema...")
        
        # Remove old database
        if self.db_path.exists():
            os.remove(self.db_path)
            
        # Create new database with upgraded schema
        conn = sqlite3.connect(self.db_path)
        
        try:
            with open(self.new_schema_path, 'r') as f:
                schema_sql = f.read()
                
            # Execute schema creation
            conn.executescript(schema_sql)
            print("✅ New schema created successfully")
            
        except Exception as e:
            print(f"❌ Error creating new schema: {e}")
            raise
            
        finally:
            conn.close()
            
    def migrate_data(self, old_data):
        """Migrate existing data to new schema"""
        if not old_data:
            print("No existing data to migrate")
            return
            
        print("🔄 Migrating existing data to new schema...")
        
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Clear sample data first
            conn.execute("DELETE FROM authors")
            conn.execute("DELETE FROM categories") 
            conn.execute("DELETE FROM trending_topics")
            
            # Migrate authors with field mapping
            for author in old_data.get('authors', []):
                # Map old fields to new schema
                author_data = {
                    'id': author.get('id'),
                    'name': author.get('name'),
                    'slug': author.get('slug'),
                    'bio': author.get('bio'),
                    'expertise': author.get('expertise'),
                    'twitter': author.get('twitter_handle'),  # Field name changed
                    'linkedin': author.get('linkedin_url'),   # Field name changed
                    'created_at': author.get('created_at'),
                    'updated_at': author.get('updated_at'),
                    # New fields get defaults
                    'title': None,
                    'email': None,
                    'location': None,
                    'image_url': None,
                    'joined_date': author.get('created_at'),
                    'article_count': 0,
                    'rating': 0.0,
                    'is_active': 1
                }
                
                conn.execute("""
                    INSERT INTO authors (id, name, slug, title, bio, email, location, 
                                       expertise, twitter, linkedin, image_url, joined_date,
                                       article_count, rating, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    author_data['id'], author_data['name'], author_data['slug'],
                    author_data['title'], author_data['bio'], author_data['email'],
                    author_data['location'], author_data['expertise'], author_data['twitter'],
                    author_data['linkedin'], author_data['image_url'], author_data['joined_date'],
                    author_data['article_count'], author_data['rating'], author_data['is_active'],
                    author_data['created_at'], author_data['updated_at']
                ))
                
            print(f"   ✅ Migrated {len(old_data.get('authors', []))} authors")
            
            # Migrate categories with field mapping
            for category in old_data.get('categories', []):
                category_data = {
                    'id': category.get('id'),
                    'name': category.get('name'),
                    'slug': category.get('slug'),
                    'description': category.get('description'),
                    'icon': category.get('icon', '📁'),
                    'article_count': category.get('article_count', 0),
                    'created_at': category.get('created_at'),
                    'updated_at': category.get('updated_at'),
                    # New fields
                    'color': '#6B7280',
                    'parent_id': None,
                    'sort_order': 999,
                    'is_featured': 0
                }
                
                conn.execute("""
                    INSERT INTO categories (id, name, slug, description, color, icon,
                                          parent_id, sort_order, article_count, is_featured,
                                          created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    category_data['id'], category_data['name'], category_data['slug'],
                    category_data['description'], category_data['color'], category_data['icon'],
                    category_data['parent_id'], category_data['sort_order'], 
                    category_data['article_count'], category_data['is_featured'],
                    category_data['created_at'], category_data['updated_at']
                ))
                
            print(f"   ✅ Migrated {len(old_data.get('categories', []))} categories")
            
            # Migrate articles with field mapping
            for article in old_data.get('articles', []):
                article_data = {
                    'id': article.get('id'),
                    'title': article.get('title'),
                    'slug': article.get('slug'),
                    'content': article.get('content'),
                    'author_id': article.get('author_id'),
                    'category_id': article.get('category_id'),
                    'tags': article.get('tags'),
                    'views': article.get('view_count', 0),  # Field name changed
                    'read_time_minutes': article.get('read_time', 0),  # Field name changed
                    'publish_date': article.get('publication_date'),  # Field name changed
                    'created_at': article.get('created_at'),
                    'updated_at': article.get('updated_at'),
                    # New fields
                    'excerpt': article.get('subtitle'),  # Use subtitle as excerpt
                    'status': 'published',  # Default to published
                    'featured': 0,
                    'trending': 0,
                    'image_url': None,
                    'hero_image_url': None,
                    'thumbnail_url': None,
                    'likes': 0,
                    'comments': 0,
                    'seo_title': article.get('title'),
                    'seo_description': article.get('meta_description')
                }
                
                conn.execute("""
                    INSERT INTO articles (id, title, slug, excerpt, content, author_id, category_id,
                                        status, featured, trending, publish_date, image_url, hero_image_url,
                                        thumbnail_url, tags, views, likes, comments, read_time_minutes,
                                        seo_title, seo_description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article_data['id'], article_data['title'], article_data['slug'],
                    article_data['excerpt'], article_data['content'], article_data['author_id'],
                    article_data['category_id'], article_data['status'], article_data['featured'],
                    article_data['trending'], article_data['publish_date'], article_data['image_url'],
                    article_data['hero_image_url'], article_data['thumbnail_url'], article_data['tags'],
                    article_data['views'], article_data['likes'], article_data['comments'],
                    article_data['read_time_minutes'], article_data['seo_title'], 
                    article_data['seo_description'], article_data['created_at'], article_data['updated_at']
                ))
                
            print(f"   ✅ Migrated {len(old_data.get('articles', []))} articles")
            
            # Migrate trending topics
            for topic in old_data.get('trending', []):
                topic_data = {
                    'id': topic.get('id'),
                    'title': topic.get('title'),
                    'slug': topic.get('slug'),
                    'description': topic.get('description'),
                    'content': topic.get('content'),
                    'heat_score': topic.get('heat_score', 0),
                    'growth_rate': topic.get('growth_rate', 0.0),
                    'momentum': topic.get('momentum', 0.0),
                    'article_count': topic.get('article_count', 0),
                    'related_articles': topic.get('related_articles'),
                    'hashtag': topic.get('hashtag'),
                    'icon': topic.get('icon', '🔥'),
                    'category_id': topic.get('category_id'),
                    'start_date': topic.get('start_date'),
                    'peak_date': topic.get('peak_date'),
                    'status': topic.get('status', 'active'),
                    'mentions_youtube': topic.get('mentions_youtube', 0),
                    'mentions_tiktok': topic.get('mentions_tiktok', 0),
                    'mentions_instagram': topic.get('mentions_instagram', 0),
                    'mentions_twitter': topic.get('mentions_twitter', 0),
                    'mentions_twitch': topic.get('mentions_twitch', 0),
                    'is_active': topic.get('is_active', 1),
                    'created_at': topic.get('created_at'),
                    'updated_at': topic.get('updated_at')
                }
                
                conn.execute("""
                    INSERT INTO trending_topics (id, title, slug, description, content, heat_score, 
                                               growth_rate, momentum, article_count, related_articles,
                                               hashtag, icon, category_id, start_date, peak_date, status,
                                               mentions_youtube, mentions_tiktok, mentions_instagram,
                                               mentions_twitter, mentions_twitch, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    topic_data['id'], topic_data['title'], topic_data['slug'], topic_data['description'],
                    topic_data['content'], topic_data['heat_score'], topic_data['growth_rate'],
                    topic_data['momentum'], topic_data['article_count'], topic_data['related_articles'],
                    topic_data['hashtag'], topic_data['icon'], topic_data['category_id'],
                    topic_data['start_date'], topic_data['peak_date'], topic_data['status'],
                    topic_data['mentions_youtube'], topic_data['mentions_tiktok'], topic_data['mentions_instagram'],
                    topic_data['mentions_twitter'], topic_data['mentions_twitch'], topic_data['is_active'],
                    topic_data['created_at'], topic_data['updated_at']
                ))
                
            print(f"   ✅ Migrated {len(old_data.get('trending', []))} trending topics")
            
            # Migrate images
            for image in old_data.get('images', []):
                image_data = {
                    'id': image.get('id'),
                    'filename': image.get('filename'),
                    'url': image.get('url'),
                    'alt_text': image.get('alt_text'),
                    'caption': image.get('caption'),
                    'content_type': image.get('content_type'),
                    'content_id': image.get('content_id'),
                    'image_type': image.get('image_type', 'hero'),
                    'file_size': image.get('file_size', 0),
                    'width': image.get('width', 0),
                    'height': image.get('height', 0),
                    'is_processed': image.get('is_processed', 0),
                    'created_at': image.get('created_at'),
                    'updated_at': image.get('updated_at')
                }
                
                conn.execute("""
                    INSERT INTO images (id, filename, url, alt_text, caption, content_type, content_id,
                                      image_type, file_size, width, height, is_processed, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    image_data['id'], image_data['filename'], image_data['url'], image_data['alt_text'],
                    image_data['caption'], image_data['content_type'], image_data['content_id'],
                    image_data['image_type'], image_data['file_size'], image_data['width'],
                    image_data['height'], image_data['is_processed'], image_data['created_at'],
                    image_data['updated_at']
                ))
                
            print(f"   ✅ Migrated {len(old_data.get('images', []))} images")
            
            # Migrate article sections
            for section in old_data.get('sections', []):
                section_data = {
                    'id': section.get('id'),
                    'article_id': section.get('article_id'),
                    'section_title': section.get('section_title'),
                    'content': section.get('content'),
                    'section_order': section.get('section_order', 1),
                    'section_type': section.get('section_type', 'text'),
                    'created_at': section.get('created_at'),
                    'updated_at': section.get('updated_at')
                }
                
                conn.execute("""
                    INSERT INTO article_sections (id, article_id, section_title, content, section_order,
                                                section_type, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    section_data['id'], section_data['article_id'], section_data['section_title'],
                    section_data['content'], section_data['section_order'], section_data['section_type'],
                    section_data['created_at'], section_data['updated_at']
                ))
                
            print(f"   ✅ Migrated {len(old_data.get('sections', []))} article sections")
            
            # Migrate related articles
            for relation in old_data.get('related', []):
                relation_data = {
                    'id': relation.get('id'),
                    'article_id': relation.get('article_id'),
                    'related_article_id': relation.get('related_article_id'),
                    'relation_strength': relation.get('relation_strength', 1.0),
                    'created_at': relation.get('created_at')
                }
                
                conn.execute("""
                    INSERT INTO related_articles (id, article_id, related_article_id, relation_strength, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    relation_data['id'], relation_data['article_id'], relation_data['related_article_id'],
                    relation_data['relation_strength'], relation_data['created_at']
                ))
                
            print(f"   ✅ Migrated {len(old_data.get('related', []))} related article relationships")
            
            # Commit all changes
            conn.commit()
            print("✅ Data migration completed successfully")
            
        except Exception as e:
            print(f"❌ Error migrating data: {e}")
            conn.rollback()
            raise
            
        finally:
            conn.close()
            
    def verify_migration(self):
        """Verify the migration was successful"""
        print("🔍 Verifying migration...")
        
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Check table structure
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['authors', 'categories', 'articles', 'trending_topics', 
                             'images', 'article_sections', 'related_articles', 'articles_fts']
            
            for table in expected_tables:
                if table in tables:
                    print(f"   ✅ Table '{table}' exists")
                else:
                    print(f"   ❌ Table '{table}' missing")
                    
            # Check some key columns exist
            cursor = conn.execute("PRAGMA table_info(authors)")
            author_columns = [row[1] for row in cursor.fetchall()]
            
            if 'email' in author_columns and 'rating' in author_columns:
                print("   ✅ New author fields present")
            else:
                print("   ❌ New author fields missing")
                
            print("🎉 Migration verification completed")
            
        except Exception as e:
            print(f"❌ Error verifying migration: {e}")
            
        finally:
            conn.close()
            
    def migrate(self):
        """Execute complete migration process"""
        print("🚀 Starting Database Schema Migration")
        print("=" * 50)
        
        try:
            # Step 1: Backup
            self.backup_database()
            
            # Step 2: Extract existing data
            old_data = self.extract_existing_data()
            
            # Step 3: Create new database
            self.create_new_database()
            
            # Step 4: Migrate data
            self.migrate_data(old_data)
            
            # Step 5: Verify
            self.verify_migration()
            
            print("\n🎉 Schema migration completed successfully!")
            print(f"📦 Backup saved as: {self.backup_path}")
            print("📋 Database now matches comprehensive documentation")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            print(f"📦 Restore from backup: {self.backup_path}")
            raise

if __name__ == "__main__":
    migrator = SchemaMigrator()
    migrator.migrate()