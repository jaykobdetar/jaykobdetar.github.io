#!/usr/bin/env python3
"""
Static Page Integrator
======================
Handles site branding for static HTML pages (search.html, authors.html, etc.)
"""

from pathlib import Path
from typing import List
try:
    from .base_integrator import BaseIntegrator
except ImportError:
    from src.integrators.base_integrator import BaseIntegrator


class StaticPageIntegrator(BaseIntegrator):
    """Integrator for applying site branding to static pages"""
    
    def __init__(self):
        super().__init__('static', 'static')
        self.static_pages = [
            'search.html',
            'authors.html'
        ]
    
    def sync_all(self):
        """Apply site branding to all static pages"""
        self.update_progress("Starting static page sync...")
        
        try:
            updated_count = 0
            for page in self.static_pages:
                if self.update_static_page(page):
                    updated_count += 1
            
            self.update_progress(f"Updated {updated_count} static pages successfully")
            
        except Exception as e:
            self.update_progress(f"Error syncing static pages: {e}")
            raise
    
    def update_static_page(self, page_name: str) -> bool:
        """Update a single static page with site branding"""
        try:
            page_path = Path(page_name)
            if not page_path.exists():
                self.update_progress(f"Warning: {page_name} not found, skipping")
                return False
            
            # Read current content
            with open(page_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply site branding
            updated_content = self._apply_site_branding(content)
            
            # Write back if changed
            if updated_content != content:
                with open(page_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                self.update_progress(f"Updated {page_name}")
                return True
            else:
                self.update_progress(f"No changes needed for {page_name}")
                return False
                
        except Exception as e:
            self.update_progress(f"Error updating {page_name}: {e}")
            return False
    
    def _apply_site_branding(self, html_content: str) -> str:
        """Apply site configuration to HTML content"""
        try:
            site_integrator = self.get_site_integrator()
            branding = site_integrator.get_config_section('branding')
            contact = site_integrator.get_config_section('contact')
            
            # Create replacements dictionary - use site config dynamically
            replacements = {
                # Site name replacements
                'Influencer News': branding.get('site_name'),
                # Title tag replacements
                ' - Influencer News': f" - {branding.get('site_name')}",
                '| Influencer News': f"| {branding.get('site_name')}",
                # Header logo text
                '>IN<': f">{branding.get('logo_text')}<",
                # Header tagline
                'Breaking stories • Real insights': branding.get('site_tagline'),
                'Breaking • Insights • Culture': branding.get('site_tagline'),
                # Theme color hex codes - comprehensive replacement
                '#4f46e5': branding.get('theme_color'),  # indigo-500
                '#6366f1': branding.get('theme_color'),  # indigo-500 variant
                '#312e81': branding.get('theme_color'),  # indigo-900
                '#4338ca': branding.get('theme_color'),  # indigo-700
                '#3730a3': branding.get('theme_color'),  # indigo-800
                '#1e1b4b': branding.get('theme_color'),  # indigo-950
                '#667eea': branding.get('theme_color'),  # custom indigo
                # Specific Tailwind class replacements - more precise
                'bg-indigo-900': f"bg-{self._get_theme_class_name(branding.get('theme_color'))}900",
                'bg-indigo-800': f"bg-{self._get_theme_class_name(branding.get('theme_color'))}800",
                'bg-indigo-700': f"bg-{self._get_theme_class_name(branding.get('theme_color'))}700",
                'bg-indigo-600': f"bg-{self._get_theme_class_name(branding.get('theme_color'))}600",
                'bg-indigo-500': f"bg-{self._get_theme_class_name(branding.get('theme_color'))}500",
                'bg-indigo-400': f"bg-{self._get_theme_class_name(branding.get('theme_color'))}400",
                'bg-indigo-300': f"bg-{self._get_theme_class_name(branding.get('theme_color'))}300",
                'bg-indigo-200': f"bg-{self._get_theme_class_name(branding.get('theme_color'))}200",
                'bg-indigo-100': f"bg-{self._get_theme_class_name(branding.get('theme_color'))}100",
                'bg-indigo-50': f"bg-{self._get_theme_class_name(branding.get('theme_color'))}50",
                'text-indigo-900': f"text-{self._get_theme_class_name(branding.get('theme_color'))}900",
                'text-indigo-800': f"text-{self._get_theme_class_name(branding.get('theme_color'))}800",
                'text-indigo-700': f"text-{self._get_theme_class_name(branding.get('theme_color'))}700",
                'text-indigo-600': f"text-{self._get_theme_class_name(branding.get('theme_color'))}600",
                'text-indigo-500': f"text-{self._get_theme_class_name(branding.get('theme_color'))}500",
                'text-indigo-400': f"text-{self._get_theme_class_name(branding.get('theme_color'))}400",
                'text-indigo-300': f"text-{self._get_theme_class_name(branding.get('theme_color'))}300",
                'text-indigo-200': f"text-{self._get_theme_class_name(branding.get('theme_color'))}200",
                'text-indigo-100': f"text-{self._get_theme_class_name(branding.get('theme_color'))}100",
                'border-indigo-700': f"border-{self._get_theme_class_name(branding.get('theme_color'))}700",
                'border-indigo-600': f"border-{self._get_theme_class_name(branding.get('theme_color'))}600",
                'border-indigo-500': f"border-{self._get_theme_class_name(branding.get('theme_color'))}500",
                'border-indigo-400': f"border-{self._get_theme_class_name(branding.get('theme_color'))}400",
                'hover:bg-indigo-700': f"hover:bg-{self._get_theme_class_name(branding.get('theme_color'))}700",
                'hover:bg-indigo-600': f"hover:bg-{self._get_theme_class_name(branding.get('theme_color'))}600",
                'hover:text-indigo-600': f"hover:text-{self._get_theme_class_name(branding.get('theme_color'))}600",
                'hover:text-indigo-200': f"hover:text-{self._get_theme_class_name(branding.get('theme_color'))}200",
                'focus:ring-indigo-400': f"focus:ring-{self._get_theme_class_name(branding.get('theme_color'))}400",
                'from-indigo-400': f"from-{self._get_theme_class_name(branding.get('theme_color'))}400",
                'from-indigo-600': f"from-{self._get_theme_class_name(branding.get('theme_color'))}600",
                'to-purple-600': f"to-{self._get_theme_class_name(branding.get('theme_color'))}600",
                # Footer copyright
                '© 2025 Influencer News': f"© 2025 {branding.get('site_name')}",
                # Contact info updates
                'news@influencernews.com': contact.get('contact_email'),
                '(555) 123-NEWS': contact.get('contact_phone'),
                '123 Creator Avenue': contact.get('business_address'),
                'Los Angeles, CA 90210': f"{contact.get('city', 'New York')}, {contact.get('state', 'NY')} {contact.get('zip_code', '10001')}",
                # Description updates
                "The world's leading source for influencer industry news and exclusive insights.": branding.get('site_description'),
                'Get the latest influencer news': contact.get('newsletter_signup_text'),
            }
            
            # Apply all replacements
            for old_value, new_value in replacements.items():
                if old_value and new_value:  # Only replace if both values exist and are not None
                    html_content = html_content.replace(old_value, str(new_value))
            
            return html_content
            
        except Exception as e:
            print(f"Warning: Could not apply site branding to static page: {e}")
            return html_content
    
    def _get_theme_class_name(self, theme_color: str) -> str:
        """Convert theme color to appropriate Tailwind class name"""
        if not theme_color:
            return 'emerald-'
        
        # Map common colors to Tailwind classes
        color_map = {
            '#059669': 'emerald-',
            '#10b981': 'emerald-',
            '#3b82f6': 'blue-',
            '#8b5cf6': 'violet-',
            '#f59e0b': 'amber-',
            '#ef4444': 'red-',
            '#6b7280': 'gray-'
        }
        
        return color_map.get(theme_color.lower(), 'emerald-')
    
    # Required abstract methods (not used for static pages)
    def parse_content_file(self, file_path):
        """Not used for static pages"""
        pass
    
    def create_content_page(self, content):
        """Not used for static pages"""
        pass
    
    def update_listing_page(self, items):
        """Not used for static pages"""
        pass
    
    def create_sample_file(self):
        """Not used for static pages"""
        pass