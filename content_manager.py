#!/usr/bin/env python3
"""
Influencer News CMS - Content Manager
Advanced GUI application for managing all content types with sync capabilities
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
import os
import json
import shutil
from datetime import datetime
from pathlib import Path
import webbrowser
from typing import Dict, List, Optional, Tuple

# Import our existing modules
try:
    from src.database.db_manager import DatabaseManager
    from src.models.article import Article
    from src.models.author import Author
    from src.models.category import Category
    from src.models.trending import TrendingTopic
    from src.utils.image_manager import ImageManager
    from src.integrators.base_integrator import BaseIntegrator
    from src.integrators.author_integrator import AuthorIntegrator
    from src.integrators.category_integrator import CategoryIntegrator
    from src.integrators.trending_integrator import TrendingIntegrator
    from src.integrators.article_integrator import ArticleIntegrator
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure you're running from the project root directory")
    exit(1)

class ContentManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Influencer News CMS - Content Manager")
        self.root.geometry("1200x800")
        
        # Initialize database and managers
        self.db = DatabaseManager()
        self.image_manager = ImageManager()
        self.author_integrator = AuthorIntegrator()
        self.category_integrator = CategoryIntegrator()
        self.trending_integrator = TrendingIntegrator()
        self.article_integrator = ArticleIntegrator()
        
        # Current selection
        self.current_content_type = None
        self.current_item = None
        
        self.setup_ui()
        self.refresh_content()
        
    def setup_ui(self):
        """Setup the main UI"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Influencer News CMS", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Left sidebar - Content type selection
        self.setup_sidebar(main_frame)
        
        # Main content area
        self.setup_content_area(main_frame)
        
        # Right sidebar - Actions
        self.setup_actions_sidebar(main_frame)
        
        # Status bar
        self.setup_status_bar(main_frame)
        
    def setup_sidebar(self, parent):
        """Setup left sidebar with content type selection"""
        sidebar_frame = ttk.LabelFrame(parent, text="Content Types", padding="10")
        sidebar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Content type buttons
        content_types = [
            ("📰 Articles", "articles"),
            ("👤 Authors", "authors"), 
            ("📁 Categories", "categories"),
            ("🔥 Trending", "trending"),
            ("🖼️ Images", "images")
        ]
        
        for i, (label, content_type) in enumerate(content_types):
            btn = ttk.Button(sidebar_frame, text=label, 
                           command=lambda ct=content_type: self.select_content_type(ct))
            btn.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2)
            sidebar_frame.columnconfigure(0, weight=1)
            
        # Separator
        ttk.Separator(sidebar_frame, orient='horizontal').grid(row=len(content_types), 
                                                              column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Global actions
        global_actions = [
            ("🔄 Sync All", self.sync_all_content),
            ("📊 Site Stats", self.show_site_stats),
            ("🔍 Database Query", self.open_db_query),
            ("🌐 Open Site", self.open_site)
        ]
        
        for i, (label, command) in enumerate(global_actions):
            btn = ttk.Button(sidebar_frame, text=label, command=command)
            btn.grid(row=len(content_types) + 1 + i, column=0, sticky=(tk.W, tk.E), pady=2)
            
    def setup_content_area(self, parent):
        """Setup main content viewing area"""
        content_frame = ttk.LabelFrame(parent, text="Content Browser", padding="10")
        content_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)
        
        # Search bar
        search_frame = ttk.Frame(content_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_changed)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Content treeview
        self.setup_treeview(content_frame)
        
        # Content details
        self.setup_details_area(content_frame)
        
    def setup_treeview(self, parent):
        """Setup the content treeview"""
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Treeview with scrollbars
        self.tree = ttk.Treeview(tree_frame, columns=('Type', 'Title', 'Status', 'Modified'), 
                                show='tree headings', height=15)
        
        # Configure columns
        self.tree.heading('#0', text='ID')
        self.tree.heading('Type', text='Type')
        self.tree.heading('Title', text='Title/Name')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Modified', text='Modified')
        
        self.tree.column('#0', width=60)
        self.tree.column('Type', width=80)
        self.tree.column('Title', width=300)
        self.tree.column('Status', width=80)
        self.tree.column('Modified', width=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self.on_item_selected)
        self.tree.bind('<Double-1>', self.on_item_double_click)
        
    def setup_details_area(self, parent):
        """Setup content details area"""
        details_frame = ttk.LabelFrame(parent, text="Content Details", padding="10")
        details_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        details_frame.columnconfigure(0, weight=1)
        
        # Details text with scrollbar
        text_frame = ttk.Frame(details_frame)
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        text_frame.columnconfigure(0, weight=1)
        
        self.details_text = tk.Text(text_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        details_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, 
                                        command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=details_scrollbar.set)
        
        self.details_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        details_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def setup_actions_sidebar(self, parent):
        """Setup right sidebar with actions"""
        actions_frame = ttk.LabelFrame(parent, text="Actions", padding="10")
        actions_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # Content actions
        content_actions = [
            ("➕ Add New", self.add_new_content),
            ("✏️ Edit Selected", self.edit_selected_content),
            ("🗑️ Delete Selected", self.delete_selected_content),
            ("📋 Duplicate", self.duplicate_selected_content)
        ]
        
        for i, (label, command) in enumerate(content_actions):
            btn = ttk.Button(actions_frame, text=label, command=command)
            btn.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=2)
            actions_frame.columnconfigure(0, weight=1)
            
        # Separator
        ttk.Separator(actions_frame, orient='horizontal').grid(row=len(content_actions), 
                                                              column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Sync actions
        sync_actions = [
            ("🔄 Sync Selected", self.sync_selected_content),
            ("🔄 Sync Type", self.sync_content_type),
            ("📤 Export Content", self.export_content),
            ("📥 Import Content", self.import_content)
        ]
        
        for i, (label, command) in enumerate(sync_actions):
            btn = ttk.Button(actions_frame, text=label, command=command)
            btn.grid(row=len(content_actions) + 1 + i, column=0, sticky=(tk.W, tk.E), pady=2)
            
        # Separator
        ttk.Separator(actions_frame, orient='horizontal').grid(
            row=len(content_actions) + len(sync_actions) + 1, 
            column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Image actions
        image_actions = [
            ("🖼️ Manage Images", self.manage_images),
            ("📦 Download Images", self.download_images),
            ("🔍 Image Report", self.show_image_report)
        ]
        
        for i, (label, command) in enumerate(image_actions):
            btn = ttk.Button(actions_frame, text=label, command=command)
            btn.grid(row=len(content_actions) + len(sync_actions) + 2 + i, 
                    column=0, sticky=(tk.W, tk.E), pady=2)
            
    def setup_status_bar(self, parent):
        """Setup status bar"""
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(parent, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def select_content_type(self, content_type):
        """Select a content type and refresh the view"""
        self.current_content_type = content_type
        self.refresh_content()
        self.status_var.set(f"Viewing {content_type}")
        
    def refresh_content(self):
        """Refresh the content view"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not self.current_content_type:
            return
            
        try:
            if self.current_content_type == "articles":
                self.load_articles()
            elif self.current_content_type == "authors":
                self.load_authors()
            elif self.current_content_type == "categories":
                self.load_categories()
            elif self.current_content_type == "trending":
                self.load_trending()
            elif self.current_content_type == "images":
                self.load_images()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load {self.current_content_type}: {e}")
            
    def load_articles(self):
        """Load articles into treeview"""
        articles = Article.find_all()
        for article in articles:
            status = "✅ Published" if hasattr(article, 'published') and article.published else "📝 Draft"
            self.tree.insert('', 'end', text=str(article.id), 
                           values=('Article', article.title, status, 
                                 getattr(article, 'updated_at', 'Unknown')))
                                 
    def load_authors(self):
        """Load authors into treeview"""
        authors = Author.find_all()
        for author in authors:
            self.tree.insert('', 'end', text=str(author.id),
                           values=('Author', author.name, '✅ Active',
                                 getattr(author, 'updated_at', 'Unknown')))
                                 
    def load_categories(self):
        """Load categories into treeview"""
        categories = Category.find_all()
        for category in categories:
            self.tree.insert('', 'end', text=str(category.id),
                           values=('Category', category.name, '✅ Active',
                                 getattr(category, 'updated_at', 'Unknown')))
                                 
    def load_trending(self):
        """Load trending topics into treeview"""
        trending = TrendingTopic.find_all()
        for topic in trending:
            heat_status = f"🔥 {getattr(topic, 'heat_score', 0)}"
            self.tree.insert('', 'end', text=str(topic.id),
                           values=('Trending', topic.title, heat_status,
                                 getattr(topic, 'updated_at', 'Unknown')))
                                 
    def load_images(self):
        """Load images into treeview"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, content_type, content_id, image_type, local_filename, original_url
                FROM images ORDER BY content_type, content_id
            """)
            for row in cursor.fetchall():
                status = "💾 Local" if row['local_filename'] else "🌐 Remote"
                display_name = f"{row['content_type']}_{row['content_id']}_{row['image_type']}"
                self.tree.insert('', 'end', text=str(row['id']),
                               values=('Image', display_name, status, 'N/A'))
                               
    def on_search_changed(self, *args):
        """Handle search text changes"""
        search_term = self.search_var.get().lower()
        if not search_term:
            self.refresh_content()
            return
            
        # Filter visible items
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            if any(search_term in str(value).lower() for value in values):
                # Keep visible
                pass
            else:
                self.tree.detach(item)
                
    def on_item_selected(self, event):
        """Handle item selection"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        item_id = self.tree.item(item)['text']
        item_type = self.tree.item(item)['values'][0]
        
        self.current_item = (item_type, item_id)
        self.show_item_details(item_type, item_id)
        
    def show_item_details(self, item_type, item_id):
        """Show details for selected item"""
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        
        try:
            if item_type == "Article":
                article = Article.find_by_id(int(item_id))
                if article:
                    details = f"Title: {article.title}\n"
                    details += f"Author ID: {article.author_id}\n"
                    details += f"Category ID: {article.category_id}\n"
                    details += f"Content: {getattr(article, 'content', 'No content')[:200]}...\n"
                    self.details_text.insert(1.0, details)
                    
            elif item_type == "Author":
                author = Author.find_by_id(int(item_id))
                if author:
                    details = f"Name: {author.name}\n"
                    details += f"Title: {getattr(author, 'title', 'N/A')}\n"
                    details += f"Bio: {getattr(author, 'bio', 'N/A')}\n"
                    details += f"Email: {getattr(author, 'email', 'N/A')}\n"
                    details += f"Location: {getattr(author, 'location', 'N/A')}\n"
                    self.details_text.insert(1.0, details)
                    
            elif item_type == "Category":
                category = Category.find_by_id(int(item_id))
                if category:
                    details = f"Name: {category.name}\n"
                    details += f"Description: {getattr(category, 'description', 'N/A')}\n"
                    details += f"Color: {getattr(category, 'color', 'N/A')}\n"
                    self.details_text.insert(1.0, details)
                    
            elif item_type == "Trending":
                topic = TrendingTopic.find_by_id(int(item_id))
                if topic:
                    details = f"Title: {topic.title}\n"
                    details += f"Description: {getattr(topic, 'description', 'N/A')}\n"
                    details += f"Heat Score: {getattr(topic, 'heat_score', 0)}\n"
                    self.details_text.insert(1.0, details)
                    
            elif item_type == "Image":
                with self.db.get_connection() as conn:
                    cursor = conn.execute("SELECT * FROM images WHERE id = ?", (item_id,))
                    row = cursor.fetchone()
                    if row:
                        details = f"Content Type: {row['content_type']}\n"
                        details += f"Content ID: {row['content_id']}\n"
                        details += f"Image Type: {row['image_type']}\n"
                        details += f"Local File: {row['local_filename'] or 'None'}\n"
                        details += f"Original URL: {row['original_url'] or 'None'}\n"
                        self.details_text.insert(1.0, details)
                        
        except Exception as e:
            self.details_text.insert(1.0, f"Error loading details: {e}")
            
        self.details_text.config(state=tk.DISABLED)
        
    def on_item_double_click(self, event):
        """Handle double-click to edit item"""
        self.edit_selected_content()
        
    # Action methods
    def add_new_content(self):
        """Add new content"""
        if not self.current_content_type or self.current_content_type == "images":
            messagebox.showwarning("Warning", "Please select a content type first")
            return
            
        dialog = ContentDialog(self.root, self.current_content_type, None, self.db)
        if dialog.result:
            self.refresh_content()
            self.status_var.set(f"Added new {self.current_content_type[:-1]}")
            
    def edit_selected_content(self):
        """Edit selected content"""
        if not self.current_item:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
            
        item_type, item_id = self.current_item
        if item_type == "Image":
            messagebox.showinfo("Info", "Use Image Manager to edit images")
            return
            
        dialog = ContentDialog(self.root, self.current_content_type, item_id, self.db)
        if dialog.result:
            self.refresh_content()
            self.status_var.set(f"Updated {item_type.lower()}")
            
    def delete_selected_content(self):
        """Delete selected content"""
        if not self.current_item:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
            
        item_type, item_id = self.current_item
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete this {item_type.lower()}?"):
            try:
                if item_type == "Article":
                    Article.delete_by_id(int(item_id))
                elif item_type == "Author":
                    Author.delete_by_id(int(item_id))
                elif item_type == "Category":
                    Category.delete_by_id(int(item_id))
                elif item_type == "Trending":
                    TrendingTopic.delete_by_id(int(item_id))
                    
                self.refresh_content()
                self.status_var.set(f"Deleted {item_type.lower()}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {e}")
                
    def duplicate_selected_content(self):
        """Duplicate selected content"""
        messagebox.showinfo("Info", "Duplicate functionality coming soon")
        
    def sync_selected_content(self):
        """Sync selected content to HTML"""
        if not self.current_item:
            messagebox.showwarning("Warning", "Please select an item to sync")
            return
            
        try:
            if self.current_content_type == "authors":
                self.author_integrator.sync_all()
                self.status_var.set("Synced selected author")
            else:
                messagebox.showinfo("Info", f"Sync for {self.current_content_type} coming soon")
                
        except Exception as e:
            messagebox.showerror("Error", f"Sync failed: {e}")
            
    def sync_content_type(self):
        """Sync all content of current type"""
        if not self.current_content_type:
            messagebox.showwarning("Warning", "Please select a content type first")
            return
            
        try:
            if self.current_content_type == "authors":
                self.author_integrator.sync_all()
                self.status_var.set("Synced all authors")
            elif self.current_content_type == "categories":
                self.category_integrator.sync_all()
                self.status_var.set("Synced all categories")
            elif self.current_content_type == "trending":
                self.trending_integrator.sync_all()
                self.status_var.set("Synced all trending topics")
            elif self.current_content_type == "articles":
                self.article_integrator.sync_all()
                self.status_var.set("Synced all articles")
            else:
                messagebox.showinfo("Info", f"Sync for {self.current_content_type} not implemented yet")
                
        except Exception as e:
            messagebox.showerror("Error", f"Sync failed: {e}")
            
    def sync_all_content(self):
        """Sync all content types"""
        try:
            # Show progress dialog
            progress_window = tk.Toplevel(self.root)
            progress_window.title("Syncing Content")
            progress_window.geometry("400x200")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            progress_label = ttk.Label(progress_window, text="Starting sync...")
            progress_label.pack(pady=20)
            
            progress_bar = ttk.Progressbar(progress_window, mode='determinate', length=300)
            progress_bar.pack(pady=10)
            progress_bar['maximum'] = 4
            
            # Sync all integrators
            integrators = [
                ("Authors", self.author_integrator),
                ("Categories", self.category_integrator), 
                ("Trending Topics", self.trending_integrator),
                ("Articles", self.article_integrator)
            ]
            
            for i, (name, integrator) in enumerate(integrators):
                progress_label.config(text=f"Syncing {name}...")
                progress_window.update()
                
                try:
                    integrator.sync_all()
                    progress_bar['value'] = i + 1
                    progress_window.update()
                except Exception as e:
                    progress_window.destroy()
                    messagebox.showerror("Error", f"Failed to sync {name}: {e}")
                    return
            
            progress_window.destroy()
            self.status_var.set("All content synced successfully")
            messagebox.showinfo("Success", "All content synced successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Sync failed: {e}")
            
    def export_content(self):
        """Export content to file"""
        messagebox.showinfo("Info", "Export functionality coming soon")
        
    def import_content(self):
        """Import content from file"""
        messagebox.showinfo("Info", "Import functionality coming soon")
        
    def manage_images(self):
        """Open image management dialog"""
        dialog = ImageManagerDialog(self.root, self.db, self.image_manager)
        
    def download_images(self):
        """Download images from procurement list"""
        messagebox.showinfo("Info", "Automatic image download coming soon\nPlease use the procurement CSV file for now")
        
    def show_image_report(self):
        """Show image status report"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT 
                        content_type,
                        COUNT(*) as total,
                        SUM(CASE WHEN local_filename IS NOT NULL THEN 1 ELSE 0 END) as local,
                        SUM(CASE WHEN original_url IS NOT NULL THEN 1 ELSE 0 END) as remote
                    FROM images 
                    GROUP BY content_type
                """)
                
                report = "Image Status Report\n" + "="*30 + "\n\n"
                for row in cursor.fetchall():
                    report += f"{row['content_type'].title()}:\n"
                    report += f"  Total: {row['total']}\n"
                    report += f"  Local: {row['local']}\n" 
                    report += f"  Remote: {row['remote']}\n\n"
                    
                messagebox.showinfo("Image Report", report)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
            
    def show_site_stats(self):
        """Show site statistics"""
        try:
            stats = {}
            stats['articles'] = len(Article.find_all())
            stats['authors'] = len(Author.find_all())
            stats['categories'] = len(Category.find_all())
            stats['trending'] = len(TrendingTopic.find_all())
            
            with self.db.get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) as count FROM images")
                stats['images'] = cursor.fetchone()['count']
                
            report = "Site Statistics\n" + "="*20 + "\n\n"
            for content_type, count in stats.items():
                report += f"{content_type.title()}: {count}\n"
                
            messagebox.showinfo("Site Statistics", report)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get statistics: {e}")
            
    def open_db_query(self):
        """Open database query dialog"""
        dialog = DatabaseQueryDialog(self.root, self.db)
        
    def open_site(self):
        """Open the website in browser"""
        site_path = Path("index.html").absolute()
        webbrowser.open(f"file://{site_path}")
        self.status_var.set("Opened site in browser")


class ContentDialog:
    """Dialog for adding/editing content"""
    def __init__(self, parent, content_type, item_id, db):
        self.result = False
        self.content_type = content_type
        self.item_id = item_id
        self.db = db
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{'Edit' if item_id else 'Add'} {content_type[:-1].title()}")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog()
        self.load_data()
        
    def setup_dialog(self):
        """Setup dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Form fields
        self.fields = {}
        
        if self.content_type == "authors":
            self.setup_author_fields(main_frame)
        elif self.content_type == "categories":
            self.setup_category_fields(main_frame)
        elif self.content_type == "trending":
            self.setup_trending_fields(main_frame)
        elif self.content_type == "articles":
            self.setup_article_fields(main_frame)
            
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
        
    def setup_author_fields(self, parent):
        """Setup author form fields"""
        fields_info = [
            ("Name", "name", "entry"),
            ("Title", "title", "entry"),
            ("Bio", "bio", "text"),
            ("Email", "email", "entry"),
            ("Location", "location", "entry"),
            ("Expertise", "expertise", "entry"),
            ("Twitter", "twitter", "entry"),
            ("LinkedIn", "linkedin", "entry")
        ]
        
        for i, (label, field, widget_type) in enumerate(fields_info):
            ttk.Label(parent, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, pady=2)
            
            if widget_type == "entry":
                var = tk.StringVar()
                widget = ttk.Entry(parent, textvariable=var, width=50)
                widget.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
                self.fields[field] = var
            elif widget_type == "text":
                widget = tk.Text(parent, width=40, height=4)
                widget.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
                self.fields[field] = widget
                
        parent.columnconfigure(1, weight=1)
        
    def setup_category_fields(self, parent):
        """Setup category form fields"""
        fields_info = [
            ("Name", "name", "entry"),
            ("Description", "description", "text"),
            ("Color", "color", "entry")
        ]
        
        for i, (label, field, widget_type) in enumerate(fields_info):
            ttk.Label(parent, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, pady=2)
            
            if widget_type == "entry":
                var = tk.StringVar()
                widget = ttk.Entry(parent, textvariable=var, width=50)
                widget.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
                self.fields[field] = var
            elif widget_type == "text":
                widget = tk.Text(parent, width=40, height=4)
                widget.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
                self.fields[field] = widget
                
        parent.columnconfigure(1, weight=1)
        
    def setup_trending_fields(self, parent):
        """Setup trending form fields"""
        fields_info = [
            ("Title", "title", "entry"),
            ("Description", "description", "text"),
            ("Heat Score", "heat_score", "entry")
        ]
        
        for i, (label, field, widget_type) in enumerate(fields_info):
            ttk.Label(parent, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, pady=2)
            
            if widget_type == "entry":
                var = tk.StringVar()
                widget = ttk.Entry(parent, textvariable=var, width=50)
                widget.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
                self.fields[field] = var
            elif widget_type == "text":
                widget = tk.Text(parent, width=40, height=4)
                widget.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
                self.fields[field] = widget
                
        parent.columnconfigure(1, weight=1)
        
    def setup_article_fields(self, parent):
        """Setup article form fields"""
        messagebox.showinfo("Info", "Article editing coming soon")
        self.dialog.destroy()
        
    def load_data(self):
        """Load existing data for editing"""
        if not self.item_id:
            return
            
        try:
            if self.content_type == "authors":
                author = Author.find_by_id(int(self.item_id))
                if author:
                    self.fields['name'].set(author.name)
                    self.fields['title'].set(getattr(author, 'title', ''))
                    self.fields['bio'].insert(1.0, getattr(author, 'bio', ''))
                    self.fields['email'].set(getattr(author, 'email', ''))
                    self.fields['location'].set(getattr(author, 'location', ''))
                    self.fields['expertise'].set(getattr(author, 'expertise', ''))
                    self.fields['twitter'].set(getattr(author, 'twitter', ''))
                    self.fields['linkedin'].set(getattr(author, 'linkedin', ''))
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
            
    def save(self):
        """Save the content"""
        try:
            if self.content_type == "authors":
                self.save_author()
            elif self.content_type == "categories":
                self.save_category()
            elif self.content_type == "trending":
                self.save_trending()
                
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")
            
    def save_author(self):
        """Save author data"""
        data = {
            'name': self.fields['name'].get(),
            'title': self.fields['title'].get(),
            'bio': self.fields['bio'].get(1.0, tk.END).strip(),
            'email': self.fields['email'].get(),
            'location': self.fields['location'].get(),
            'expertise': self.fields['expertise'].get(),
            'twitter': self.fields['twitter'].get(),
            'linkedin': self.fields['linkedin'].get()
        }
        
        if self.item_id:
            # Update existing
            Author.update(int(self.item_id), **data)
        else:
            # Create new
            Author.create(**data)
            
    def save_category(self):
        """Save category data"""
        data = {
            'name': self.fields['name'].get(),
            'description': self.fields['description'].get(1.0, tk.END).strip(),
            'color': self.fields['color'].get()
        }
        
        if self.item_id:
            Category.update(int(self.item_id), **data)
        else:
            Category.create(**data)
            
    def save_trending(self):
        """Save trending data"""
        data = {
            'title': self.fields['title'].get(),
            'description': self.fields['description'].get(1.0, tk.END).strip(),
            'heat_score': int(self.fields['heat_score'].get() or 0)
        }
        
        if self.item_id:
            TrendingTopic.update(int(self.item_id), **data)
        else:
            TrendingTopic.create(**data)
            
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()


class ImageManagerDialog:
    """Dialog for managing images"""
    def __init__(self, parent, db, image_manager):
        self.db = db
        self.image_manager = image_manager
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Image Manager")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        
        self.setup_dialog()
        
    def setup_dialog(self):
        """Setup image manager dialog"""
        ttk.Label(self.dialog, text="Image Manager", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        ttk.Label(self.dialog, 
                 text="Use the procurement CSV file to source images").pack(pady=10)
        
        # Show procurement list location
        procurement_file = Path("data/image_procurement_list.csv")
        if procurement_file.exists():
            ttk.Label(self.dialog, 
                     text=f"Procurement list: {procurement_file.absolute()}").pack(pady=5)
            
        ttk.Button(self.dialog, text="Close", 
                  command=self.dialog.destroy).pack(pady=20)


class DatabaseQueryDialog:
    """Dialog for database queries"""
    def __init__(self, parent, db):
        self.db = db
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Database Query")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        
        self.setup_dialog()
        
    def setup_dialog(self):
        """Setup query dialog"""
        ttk.Label(self.dialog, text="Database Query", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Query input
        ttk.Label(self.dialog, text="SQL Query:").pack(anchor=tk.W, padx=20)
        self.query_text = tk.Text(self.dialog, height=6, width=70)
        self.query_text.pack(padx=20, pady=5)
        
        # Execute button
        ttk.Button(self.dialog, text="Execute", 
                  command=self.execute_query).pack(pady=10)
        
        # Results
        ttk.Label(self.dialog, text="Results:").pack(anchor=tk.W, padx=20)
        self.results_text = tk.Text(self.dialog, height=15, width=70)
        self.results_text.pack(padx=20, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.dialog, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
    def execute_query(self):
        """Execute the SQL query"""
        query = self.query_text.get(1.0, tk.END).strip()
        if not query:
            return
            
        try:
            with self.db.get_connection() as conn:
                cursor = conn.execute(query)
                results = cursor.fetchall()
                
                self.results_text.delete(1.0, tk.END)
                
                if results:
                    # Show column headers
                    if hasattr(cursor, 'description') and cursor.description:
                        headers = [desc[0] for desc in cursor.description]
                        self.results_text.insert(tk.END, " | ".join(headers) + "\n")
                        self.results_text.insert(tk.END, "-" * 50 + "\n")
                    
                    # Show results
                    for row in results:
                        if hasattr(row, 'keys'):
                            self.results_text.insert(tk.END, " | ".join(str(row[key]) for key in row.keys()) + "\n")
                        else:
                            self.results_text.insert(tk.END, " | ".join(str(val) for val in row) + "\n")
                else:
                    self.results_text.insert(tk.END, "Query executed successfully. No results returned.")
                    
        except Exception as e:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Error: {e}")


def main():
    """Main function"""
    root = tk.Tk()
    app = ContentManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()