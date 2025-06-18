#!/usr/bin/env python3
"""
Simple Template Engine for Influencer News CMS
Provides safe template rendering with variable substitution
"""

import re
import html
from typing import Dict, Any, Optional
import os

class TemplateEngine:
    """Simple template engine with variable substitution"""
    
    def __init__(self, template_dir: Optional[str] = None):
        self.template_dir = template_dir or os.path.join(
            os.path.dirname(__file__), '..', '..', 'templates'
        )
        self.cache = {}
    
    def load_template(self, template_name: str) -> str:
        """Load template from file with caching"""
        if template_name in self.cache:
            return self.cache[template_name]
        
        template_path = os.path.join(self.template_dir, template_name)
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        self.cache[template_name] = template
        return template
    
    def render(self, template: str, context: Dict[str, Any]) -> str:
        """
        Render template with context variables
        Supports:
        - {{variable}} - Simple variable substitution with HTML escaping
        - {{!variable}} - Raw variable substitution (no escaping)
        - {{#if variable}}...{{/if}} - Conditional blocks
        - {{#each array}}...{{/each}} - Loop blocks with {{this}} for current item
        """
        
        # Process conditionals
        template = self._process_conditionals(template, context)
        
        # Process loops
        template = self._process_loops(template, context)
        
        # Process variables
        template = self._process_variables(template, context)
        
        return template
    
    def render_file(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render template from file"""
        template = self.load_template(template_name)
        return self.render(template, context)
    
    def _process_conditionals(self, template: str, context: Dict[str, Any]) -> str:
        """Process {{#if}} conditionals"""
        pattern = r'\{\{#if\s+(\w+(?:\.\w+)*)\}\}(.*?)\{\{/if\}\}'
        
        def replace_conditional(match):
            var_name = match.group(1)
            content = match.group(2)
            
            value = self._get_nested_value(context, var_name)
            if value:
                return content
            return ''
        
        return re.sub(pattern, replace_conditional, template, flags=re.DOTALL)
    
    def _process_loops(self, template: str, context: Dict[str, Any]) -> str:
        """Process {{#each}} loops"""
        pattern = r'\{\{#each\s+(\w+(?:\.\w+)*)\}\}(.*?)\{\{/each\}\}'
        
        def replace_loop(match):
            var_name = match.group(1)
            content = match.group(2)
            
            items = self._get_nested_value(context, var_name)
            if not items or not hasattr(items, '__iter__'):
                return ''
            
            result = []
            for item in items:
                # Create new context with 'this' pointing to current item
                loop_context = context.copy()
                loop_context['this'] = item
                
                # Process the loop content with the loop context
                loop_content = self._process_variables(content, loop_context)
                result.append(loop_content)
            
            return ''.join(result)
        
        return re.sub(pattern, replace_loop, template, flags=re.DOTALL)
    
    def _process_variables(self, template: str, context: Dict[str, Any]) -> str:
        """Process {{variable}} substitutions"""
        
        # Raw variables (no escaping) - process first to avoid conflicts
        pattern_raw = r'\{\{!([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\}\}'
        template = re.sub(pattern_raw, 
                         lambda m: str(self._get_nested_value(context, m.group(1)) or ''), 
                         template)
        
        # Escaped variables - process after raw variables
        pattern_escaped = r'\{\{([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\}\}'
        template = re.sub(pattern_escaped, 
                         lambda m: html.escape(str(self._get_nested_value(context, m.group(1)) or '')), 
                         template)
        
        return template
    
    def _get_nested_value(self, obj: Dict[str, Any], path: str) -> Any:
        """Get nested value from object using dot notation"""
        parts = path.split('.')
        current = obj
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif hasattr(current, part):
                current = getattr(current, part)
            else:
                return None
        
        return current


class ArticleTemplate(TemplateEngine):
    """Specialized template engine for articles"""
    
    def __init__(self):
        super().__init__()
        self.article_template = None
    
    def load_article_template(self, template_path: str):
        """Load the main article template"""
        with open(template_path, 'r', encoding='utf-8') as f:
            self.article_template = f.read()
    
    def render_article(self, article_data: Dict[str, Any], base_path: str = '../../') -> str:
        """Render article with proper data structure"""
        
        # Prepare context with all needed data
        context = {
            'base_path': base_path,
            'article': article_data,
            'meta': {
                'title': f"{article_data['title']} - Influencer News",
                'description': article_data.get('excerpt', ''),
                'author': article_data.get('author_name', ''),
                'publish_date': article_data.get('publish_date', ''),
            },
            'links': {
                'home': f"{base_path}index.html",
                'search': f"{base_path}search.html",
                'authors': f"{base_path}authors.html",
                'categories': f"{base_path}integrated/categories.html",
                'trending': f"{base_path}integrated/trending.html",
                'author': f"{base_path}integrated/authors/author_{article_data.get('author_slug', '')}.html",
                'category': f"{base_path}integrated/categories/category_{article_data.get('category_slug', '')}.html",
            },
            'stats': {
                'views': f"{article_data.get('views', 0):,}",
                'likes': f"{article_data.get('likes', 0):,}",
                'comments': f"{article_data.get('comments', 0):,}",
                'shares': f"{article_data.get('shares', 0):,}",
            }
        }
        
        return self.render(self.article_template, context)


def main():
    """Test the template engine"""
    engine = TemplateEngine()
    
    # Test template
    template = """
    <h1>{{title}}</h1>
    <p>By {{author.name}} ({{author.email}})</p>
    
    {{#if featured}}
    <div class="featured">This is a featured article!</div>
    {{/if}}
    
    <ul>
    {{#each tags}}
        <li>{{this}}</li>
    {{/each}}
    </ul>
    
    <div>{{!html_content}}</div>
    """
    
    context = {
        'title': 'Test Article',
        'author': {
            'name': 'John Doe',
            'email': 'john@example.com'
        },
        'featured': True,
        'tags': ['tech', 'news', 'ai'],
        'html_content': '<p>This is <strong>HTML</strong> content</p>'
    }
    
    result = engine.render(template, context)
    print(result)


if __name__ == '__main__':
    main()