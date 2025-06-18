#!/usr/bin/env python3
"""
Site Integrator
===============
Manages site-wide configuration and content from content/site/ files
"""

import os
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from .base_integrator import BaseIntegrator
    from ..models.site_config import SiteConfig
except ImportError:
    from base_integrator import BaseIntegrator
    from src.models.site_config import SiteConfig


class SiteIntegrator(BaseIntegrator):
    """Integrator for site-wide configuration and content"""
    
    def __init__(self):
        super().__init__('site', 'site')
        self._cached_config = None
        self._cache_time = None
        self._cache_duration = 300  # 5 minutes
    
    def parse_content_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse site configuration content file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Split into metadata and content sections
            if 'METADATA:' in content and 'CONTENT:' in content:
                metadata_section = content.split('METADATA:')[1].split('CONTENT:')[0]
                content_section = content.split('CONTENT:')[1]
            else:
                raise ValueError("File must contain METADATA: and CONTENT: sections")
            
            # Parse metadata
            metadata = self.parse_metadata_section(metadata_section)
            
            # Parse content based on config type
            config_type = metadata.get('type', 'unknown')
            parsed_content = self.parse_config_content(content_section.strip(), config_type)
            
            return {
                'config_type': config_type,
                'config_data': parsed_content,
                'metadata': metadata,
                'source_file': str(file_path),
                'last_modified': datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            }
            
        except Exception as e:
            self.update_progress(f"Error parsing {file_path.name}: {str(e)}")
            raise
    
    def parse_config_content(self, content: str, config_type: str) -> Dict[str, str]:
        """Parse configuration content based on type"""
        config_data = {}
        
        if config_type == 'site-branding':
            # Parse site branding configuration
            for line in content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    config_data[key] = value
                    
        elif config_type == 'site-contact':
            # Parse contact information
            for line in content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    config_data[key] = value
                    
        elif config_type == 'site-navigation':
            # Parse navigation structure
            current_section = None
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if line.endswith(':'):
                    current_section = line[:-1].lower().replace(' ', '_')
                    config_data[current_section] = []
                elif line.startswith('- '):
                    # Navigation item
                    item = line[2:]  # Remove '- '
                    if current_section and isinstance(config_data.get(current_section), list):
                        config_data[current_section].append(item)
                    elif ':' in item:
                        # Key-value pair
                        key, value = item.split(':', 1)
                        config_data[key.strip().lower().replace(' ', '_')] = value.strip()
                elif ':' in line:
                    # Direct key-value pair
                    key, value = line.split(':', 1)
                    config_data[key.strip().lower().replace(' ', '_')] = value.strip()
                    
        elif config_type == 'site-content':
            # Parse general site content
            for line in content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    config_data[key] = value
        
        return config_data
    
    def create_content_page(self, content: Any):
        """Site config doesn't generate individual pages"""
        pass
    
    def update_listing_page(self, content_list: List[Any]):
        """Site config doesn't have listing pages"""
        pass
    
    def create_sample_file(self):
        """Create sample site configuration files"""
        # Site branding sample already created in the main implementation
        pass
    
    def process_new_content(self) -> int:
        """Process all site configuration files"""
        self.update_progress("Processing site configuration files...", 0)
        processed_count = 0
        
        # Get all .txt files in site content directory
        txt_files = list(self.content_dir.glob("*.txt"))
        total_files = len(txt_files)
        
        if total_files == 0:
            self.update_progress("No site config files found.", 100)
            return 0
        
        all_config_data = {}
        
        # Process each .txt file
        for idx, file_path in enumerate(txt_files):
            progress = (idx / total_files) * 100
            
            try:
                self.update_progress(f"Processing: {file_path.name}", progress)
                
                # Parse content file
                parsed_data = self.parse_content_file(file_path)
                config_type = parsed_data['config_type']
                config_data = parsed_data['config_data']
                last_modified = parsed_data['last_modified']
                
                # Add to bulk update dictionary
                all_config_data[config_type] = config_data
                
                # Store last modified time for each config type
                SiteConfig.set_config(config_type, '_last_modified', last_modified, 
                                    f'Last modification time for {config_type}')
                
                processed_count += 1
                self.update_progress(f"Parsed: {config_type}", progress)
                
            except Exception as e:
                self.update_progress(f"Error processing {file_path.name}: {str(e)}", progress)
                continue
        
        # Bulk update all configuration
        if all_config_data:
            self.update_progress("Updating database...", 90)
            
            # Convert lists to JSON strings for navigation config
            for config_type, config_data in all_config_data.items():
                for key, value in config_data.items():
                    if isinstance(value, list):
                        all_config_data[config_type][key] = '\n'.join(value)
            
            SiteConfig.bulk_update(all_config_data)
            
            # Invalidate cache
            self._cached_config = None
            self._cache_time = None
            
            self.update_progress(f"Successfully processed {processed_count} site config files!", 100)
        
        return processed_count
    
    def sync_with_files(self) -> Dict[str, int]:
        """Sync site configuration files with database"""
        # For site config, we just process new content
        processed_count = self.process_new_content()
        return {
            'added': processed_count,
            'updated': 0,
            'removed': 0,
            'skipped': 0
        }
    
    def sync_all(self):
        """Site config doesn't generate individual pages"""
        pass
    
    def update_all_listing_pages(self):
        """Site config doesn't have listing pages"""
        pass
    
    def get_site_config(self, force_refresh: bool = False) -> Dict[str, Dict[str, str]]:
        """Get all site configuration with caching"""
        now = datetime.datetime.now()
        
        # Check cache validity
        if (not force_refresh and 
            self._cached_config and 
            self._cache_time and 
            (now - self._cache_time).seconds < self._cache_duration):
            return self._cached_config
        
        # Refresh cache
        self._cached_config = SiteConfig.get_all_config()
        self._cache_time = now
        
        return self._cached_config
    
    def get_config_by_type(self, config_type: str) -> Dict[str, str]:
        """Get configuration for specific type"""
        all_config = self.get_site_config()
        return all_config.get(config_type, {})
    
    def get_config_value(self, config_type: str, config_key: str, default: str = '') -> str:
        """Get specific configuration value"""
        config = self.get_config_by_type(config_type)
        return config.get(config_key, default)
    
    def get_branding_config(self) -> Dict[str, str]:
        """Get site branding configuration"""
        return self.get_config_by_type('site-branding')
    
    def get_contact_config(self) -> Dict[str, str]:
        """Get contact information configuration"""
        return self.get_config_by_type('site-contact')
    
    def get_navigation_config(self) -> Dict[str, str]:
        """Get navigation configuration"""
        return self.get_config_by_type('site-navigation')
    
    def get_content_config(self) -> Dict[str, str]:
        """Get general content configuration"""
        return self.get_config_by_type('site-content')
    
    def get_config_section(self, section_name: str) -> Dict[str, str]:
        """Get configuration section by name (alias for get_config_by_type)"""
        # Map section names to config types
        section_map = {
            'branding': 'site-branding',
            'contact': 'site-contact',
            'navigation': 'site-navigation',
            'content': 'site-content'
        }
        
        config_type = section_map.get(section_name, f'site-{section_name}')
        return self.get_config_by_type(config_type)
    
    def generate_site_meta_tags(self, page_title: str = None, page_description: str = None) -> str:
        """Generate meta tags for HTML pages"""
        branding = self.get_branding_config()
        
        site_name = branding.get('site_name', 'Influencer News')
        site_description = branding.get('site_description', 'The world\'s leading source for influencer industry news')
        theme_color = branding.get('theme_color', '#4f46e5')
        
        title = f"{page_title} - {site_name}" if page_title else site_name
        description = page_description or site_description
        
        return f'''<title>{self.sanitize_text(title)}</title>
    <meta name="description" content="{self.sanitize_text(description)}">
    <meta name="theme-color" content="{theme_color}">
    <meta property="og:title" content="{self.sanitize_text(title)}">
    <meta property="og:description" content="{self.sanitize_text(description)}">
    <meta property="og:site_name" content="{self.sanitize_text(site_name)}">
    <meta name="twitter:title" content="{self.sanitize_text(title)}">
    <meta name="twitter:description" content="{self.sanitize_text(description)}">'''
    
    def generate_header_html(self, current_page: str = '', path_prefix: str = '') -> str:
        """Generate header HTML with navigation"""
        branding = self.get_branding_config()
        navigation = self.get_navigation_config()
        
        site_name = branding.get('site_name', 'Influencer News')
        site_tagline = branding.get('site_tagline', 'Breaking stories • Real insights')
        logo_text = branding.get('logo_text', 'IN')
        
        # Build navigation items
        nav_items = []
        main_nav = navigation.get('main_navigation_items', '')
        
        # Handle both string (from database) and list formats
        if isinstance(main_nav, str):
            nav_lines = main_nav.split('\n') if main_nav else []
        else:
            nav_lines = main_nav if isinstance(main_nav, list) else []
        
        for item in nav_lines:
            if ':' in item:
                name, url = item.split(':', 1)
                name = name.strip()
                url = url.strip()
                
                # Add path prefix if needed
                if path_prefix and not url.startswith('http'):
                    url = f"{path_prefix}{url}"
                
                active_class = 'text-indigo-200' if current_page.lower() == name.lower() else ''
                nav_items.append(f'<li><a href="{url}" class="nav-link hover:text-indigo-200 transition font-medium {active_class}">{name}</a></li>')
        
        nav_html = '\n                    '.join(nav_items)
        
        return f'''<header class="bg-indigo-900 text-white sticky top-0 z-50 shadow-2xl">
        <div class="container mx-auto px-4 py-4 flex justify-between items-center">
            <div class="flex items-center">
                <div class="w-16 h-16 bg-gradient-to-br from-indigo-400 to-purple-600 rounded-full flex items-center justify-center mr-4">
                    <span class="text-2xl font-bold text-white">{logo_text}</span>
                </div>
                <div>
                    <h1 class="text-3xl font-bold hero-title">{site_name}</h1>
                    <p class="text-xs text-indigo-200">{site_tagline}</p>
                </div>
            </div>
            <nav class="hidden md:block">
                <ul class="flex space-x-8">
                    {nav_html}
                </ul>
            </nav>
        </div>
    </header>'''
    
    def generate_footer_html(self, path_prefix: str = '') -> str:
        """Generate footer HTML"""
        branding = self.get_branding_config()
        contact = self.get_contact_config()
        content = self.get_content_config()
        navigation = self.get_navigation_config()
        
        site_name = branding.get('site_name', 'Influencer News')
        logo_text = branding.get('logo_text', 'IN')
        site_subtitle = branding.get('site_subtitle', 'Breaking • Insights • Culture')
        footer_description = content.get('footer_description', branding.get('site_description', ''))
        copyright_text = content.get('copyright_text', f'© 2025 {site_name}. All rights reserved.')
        
        contact_email = contact.get('contact_email', 'news@influencernews.com')
        contact_phone = contact.get('contact_phone', '(555) 123-NEWS')
        business_address = contact.get('business_address', '123 Creator Avenue')
        city = contact.get('city', 'Los Angeles')
        state = contact.get('state', 'CA')
        zip_code = contact.get('zip_code', '90210')
        
        return f'''<footer class="bg-gray-900 text-white py-16 mt-16">
        <div class="container mx-auto px-4">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
                <div>
                    <div class="flex items-center mb-4">
                        <div class="w-12 h-12 bg-gradient-to-br from-indigo-400 to-purple-600 rounded-full flex items-center justify-center mr-3">
                            <span class="text-lg font-bold">{logo_text}</span>
                        </div>
                        <div>
                            <h3 class="text-xl font-bold">{site_name}</h3>
                            <p class="text-sm text-gray-400">{site_subtitle}</p>
                        </div>
                    </div>
                    <p class="text-gray-300 mb-4">{footer_description}</p>
                </div>
                <div>
                    <h3 class="text-lg font-bold mb-4">Quick Links</h3>
                    <ul class="space-y-2">
                        <li><a href="{path_prefix}index.html" class="text-gray-300 hover:text-white transition">Latest News</a></li>
                        <li><a href="{path_prefix}search.html" class="text-gray-300 hover:text-white transition">Search</a></li>
                        <li><a href="{path_prefix}authors.html" class="text-gray-300 hover:text-white transition">Authors</a></li>
                        <li><a href="{path_prefix}integrated/categories.html" class="text-gray-300 hover:text-white transition">Categories</a></li>
                    </ul>
                </div>
                <div>
                    <h3 class="text-lg font-bold mb-4">Categories</h3>
                    <ul class="space-y-2">
                        <li><a href="{path_prefix}search.html?category=business" class="text-gray-300 hover:text-white transition">💼 Business</a></li>
                        <li><a href="{path_prefix}search.html?category=entertainment" class="text-gray-300 hover:text-white transition">🎥 Entertainment</a></li>
                        <li><a href="{path_prefix}search.html?category=fashion" class="text-gray-300 hover:text-white transition">💄 Beauty & Fashion</a></li>
                        <li><a href="{path_prefix}search.html?category=technology" class="text-gray-300 hover:text-white transition">⚡ Technology</a></li>
                    </ul>
                </div>
                <div>
                    <h3 class="text-lg font-bold mb-4">Contact Info</h3>
                    <div class="space-y-3 text-gray-300">
                        <p>📧 {contact_email}</p>
                        <p>📞 {contact_phone}</p>
                        <p>📍 {business_address}<br>{city}, {state} {zip_code}</p>
                    </div>
                </div>
            </div>
            <div class="border-t border-gray-700 pt-8 text-center">
                <p class="text-gray-400 text-sm">{copyright_text}</p>
            </div>
        </div>
    </footer>'''