#!/usr/bin/env python3
"""
Comprehensive tests for content sanitization and validation
Tests for XSS prevention, HTML sanitization, and data validation
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.sanitizer import ContentSanitizer, ModelValidator, ValidationResult


class TestContentSanitizer:
    """Test the ContentSanitizer class"""
    
    def setup_method(self):
        """Setup test instance"""
        self.sanitizer = ContentSanitizer()
    
    def test_basic_sanitization(self):
        """Test basic content sanitization"""
        content = "Hello <b>world</b>!"
        result = self.sanitizer.sanitize_content(content)
        
        assert result.is_valid
        assert result.cleaned_content == "Hello world!"  # <b> removed
        assert len(result.errors) == 0
    
    def test_allowed_html_tags(self):
        """Test that allowed HTML tags are preserved"""
        content = "Hello <strong>world</strong> and <em>universe</em>!"
        result = self.sanitizer.sanitize_content(content)
        
        assert result.is_valid
        assert "<strong>" in result.cleaned_content
        assert "<em>" in result.cleaned_content
    
    def test_xss_script_injection(self):
        """Test XSS prevention - script tags"""
        dangerous_content = 'Hello <script>alert("XSS")</script> world'
        result = self.sanitizer.sanitize_content(dangerous_content)
        
        assert not result.is_valid
        assert "script" not in result.cleaned_content.lower()
        assert any("dangerous content" in error.lower() for error in result.errors)
        assert any("dangerous content was removed" in warning for warning in result.warnings)
    
    def test_xss_javascript_urls(self):
        """Test XSS prevention - javascript: URLs"""
        dangerous_content = '<a href="javascript:alert(\'XSS\')">Click me</a>'
        result = self.sanitizer.sanitize_content(dangerous_content)
        
        assert not result.is_valid
        assert "javascript:" not in result.cleaned_content
        assert any("dangerous content" in error.lower() for error in result.errors)
    
    def test_xss_event_handlers(self):
        """Test XSS prevention - event handlers"""
        dangerous_content = '<div onclick="alert(\'XSS\')">Click me</div>'
        result = self.sanitizer.sanitize_content(dangerous_content)
        
        assert not result.is_valid
        assert "onclick" not in result.cleaned_content
        assert any("dangerous content" in error.lower() for error in result.errors)
    
    def test_xss_data_urls(self):
        """Test XSS prevention - data: URLs"""
        dangerous_content = '<img src="data:text/html,<script>alert(\'XSS\')</script>">'
        result = self.sanitizer.sanitize_content(dangerous_content)
        
        assert not result.is_valid
        assert "data:" not in result.cleaned_content
        assert any("dangerous content" in error.lower() for error in result.errors)
    
    def test_iframe_removal(self):
        """Test removal of iframe tags"""
        dangerous_content = 'Safe content <iframe src="evil.com"></iframe> more content'
        result = self.sanitizer.sanitize_content(dangerous_content)
        
        assert not result.is_valid
        assert "iframe" not in result.cleaned_content.lower()
        assert any("dangerous content" in error.lower() for error in result.errors)
    
    def test_form_removal(self):
        """Test removal of form tags"""
        dangerous_content = 'Content <form><input type="password"></form> more'
        result = self.sanitizer.sanitize_content(dangerous_content)
        
        assert not result.is_valid
        assert "form" not in result.cleaned_content.lower()
        assert "input" not in result.cleaned_content.lower()
    
    def test_meta_link_removal(self):
        """Test removal of meta and link tags"""
        dangerous_content = '<meta http-equiv="refresh" content="0;url=evil.com"><link rel="stylesheet" href="evil.css">'
        result = self.sanitizer.sanitize_content(dangerous_content)
        
        assert not result.is_valid
        assert "meta" not in result.cleaned_content.lower()
        assert "link" not in result.cleaned_content.lower()
    
    def test_length_validation(self):
        """Test content length validation"""
        long_content = "x" * 100000  # Very long content
        result = self.sanitizer.sanitize_content(long_content, 'general')
        
        assert not result.is_valid
        assert len(result.cleaned_content) <= self.sanitizer.max_content_length
        assert any("exceeds maximum length" in error for error in result.errors)
        assert any("truncated" in warning for warning in result.warnings)
    
    def test_email_validation(self):
        """Test email validation"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        invalid_emails = [
            "invalid.email",
            "@domain.com",
            "user@",
            "user..name@domain.com",
            ".user@domain.com",
            "user@domain.com.",
        ]
        
        for email in valid_emails:
            result = self.sanitizer.sanitize_content(email, 'email')
            assert result.is_valid, f"Valid email {email} was rejected"
        
        for email in invalid_emails:
            result = self.sanitizer.sanitize_content(email, 'email')
            assert not result.is_valid, f"Invalid email {email} was accepted"
    
    def test_url_validation(self):
        """Test URL validation"""
        valid_urls = [
            "https://example.com",
            "http://subdomain.example.com/path",
            "https://example.com/path?query=value"
        ]
        
        invalid_urls = [
            "ftp://example.com",
            "javascript:alert('xss')",
            "data:text/html,<script>",
            "not-a-url",
        ]
        
        for url in valid_urls:
            result = self.sanitizer.sanitize_content(url, 'url')
            assert result.is_valid, f"Valid URL {url} was rejected"
        
        for url in invalid_urls:
            result = self.sanitizer.sanitize_content(url, 'url')
            assert not result.is_valid, f"Invalid URL {url} was accepted"
    
    def test_slug_validation(self):
        """Test slug validation and cleaning"""
        test_cases = [
            ("Hello World", "hello-world"),
            ("Test@#$%Content", "test-content"),
            ("Multiple   Spaces", "multiple-spaces"),
            ("--leading-trailing--", "leading-trailing"),
            ("CamelCase", "camelcase"),
        ]
        
        for input_slug, expected in test_cases:
            result = self.sanitizer.sanitize_content(input_slug, 'slug')
            assert result.is_valid
            assert result.cleaned_content == expected
    
    def test_title_validation(self):
        """Test title validation"""
        valid_titles = [
            "This is a valid title",
            "Another Great Article Title",
            "Title with Numbers 123"
        ]
        
        invalid_titles = [
            "Hi",  # Too short
            "!!???..",  # Too much punctuation
        ]
        
        for title in valid_titles:
            result = self.sanitizer.sanitize_content(title, 'title')
            assert result.is_valid, f"Valid title '{title}' was rejected"
        
        for title in invalid_titles:
            result = self.sanitizer.sanitize_content(title, 'title')
            assert not result.is_valid, f"Invalid title '{title}' was accepted"
    
    def test_href_attribute_cleaning(self):
        """Test href attribute sanitization"""
        test_cases = [
            ('href="https://example.com"', 'https://example.com'),
            ('href="javascript:alert(1)"', ''),  # Dangerous
            ('href="data:text/html"', ''),  # Dangerous
            ('href="/relative/path"', '/relative/path'),  # Safe relative
            ('href="mailto:test@example.com"', 'mailto:test@example.com'),
            ('href="tel:+1234567890"', 'tel:+1234567890'),
            ('href="#anchor"', '#anchor'),
        ]
        
        for href_attr, expected in test_cases:
            href_value = href_attr.split('"')[1]
            result = self.sanitizer._validate_href(href_value)
            assert result == expected, f"href '{href_value}' expected '{expected}', got '{result}'"
    
    def test_html_attribute_cleaning(self):
        """Test HTML attribute cleaning"""
        dangerous_html = '<a href="https://example.com" onclick="alert(1)" data-evil="bad">Link</a>'
        result = self.sanitizer.sanitize_content(dangerous_html)
        
        # Should keep safe href but remove onclick and data attributes
        assert 'href="https://example.com"' in result.cleaned_content
        assert 'onclick' not in result.cleaned_content
        assert 'data-evil' not in result.cleaned_content
    
    def test_null_byte_removal(self):
        """Test removal of null bytes"""
        content_with_nulls = "Hello\x00World\x00"
        result = self.sanitizer.sanitize_content(content_with_nulls)
        
        assert result.is_valid
        assert '\x00' not in result.cleaned_content
        assert result.cleaned_content == "HelloWorld"
    
    def test_whitespace_normalization(self):
        """Test whitespace normalization"""
        messy_content = "  Hello    world  \n\n  with   spaces  "
        result = self.sanitizer.sanitize_content(messy_content)
        
        assert result.is_valid
        assert result.cleaned_content == "Hello world with spaces"
    
    def test_non_string_input(self):
        """Test handling of non-string input"""
        inputs = [123, None, ['list'], {'dict': 'value'}]
        
        for input_val in inputs:
            result = self.sanitizer.sanitize_content(input_val)
            assert isinstance(result.cleaned_content, str)
            assert any("converted to string" in warning for warning in result.warnings)


class TestModelValidator:
    """Test the ModelValidator class"""
    
    def setup_method(self):
        """Setup test instance"""
        self.validator = ModelValidator()
    
    def test_valid_article_validation(self):
        """Test validation of valid article data"""
        article_data = {
            'title': 'Test Article Title',
            'slug': 'test-article-title',
            'content': 'This is the article content with enough text.',
            'author_id': 1,
            'category_id': 2,
            'read_time': 5,
            'tags': ['tech', 'news']
        }
        
        result = self.validator.validate_article(article_data)
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_missing_required_article_fields(self):
        """Test validation with missing required fields"""
        incomplete_data = {
            'title': 'Test Article',
            # Missing slug, content, author_id, category_id
        }
        
        result = self.validator.validate_article(incomplete_data)
        assert not result.is_valid
        assert len(result.errors) >= 4  # At least 4 missing fields
    
    def test_article_xss_in_content(self):
        """Test XSS prevention in article content"""
        article_data = {
            'title': 'Test Article',
            'slug': 'test-article',
            'content': 'Safe content <script>alert("XSS")</script> more content',
            'author_id': 1,
            'category_id': 2,
        }
        
        result = self.validator.validate_article(article_data)
        assert not result.is_valid
        assert 'script' not in result.cleaned_content['content'].lower()
        assert any('dangerous content' in error.lower() for error in result.errors)
    
    def test_article_read_time_validation(self):
        """Test read time validation"""
        test_cases = [
            (5, True),      # Valid
            (60, True),     # Valid
            (0, False),     # Too low
            (200, False),   # Too high
            ('invalid', False),  # Not a number
        ]
        
        base_data = {
            'title': 'Test Article',
            'slug': 'test-article',
            'content': 'Content',
            'author_id': 1,
            'category_id': 2,
        }
        
        for read_time, should_be_valid in test_cases:
            article_data = base_data.copy()
            article_data['read_time'] = read_time
            
            result = self.validator.validate_article(article_data)
            if should_be_valid:
                assert result.is_valid or len([e for e in result.errors if 'read time' in e.lower()]) == 0
            else:
                assert not result.is_valid or len([w for w in result.warnings if 'read time' in w.lower()]) > 0
    
    def test_article_tags_validation(self):
        """Test tags validation and sanitization"""
        article_data = {
            'title': 'Test Article',
            'slug': 'test-article', 
            'content': 'Content',
            'author_id': 1,
            'category_id': 2,
            'tags': ['tech', 'news', '<script>alert("xss")</script>', 'valid-tag'] + ['extra'] * 10
        }
        
        result = self.validator.validate_article(article_data)
        cleaned_tags = result.cleaned_content['tags']
        
        # Should remove dangerous tag and limit to 10 tags
        assert len(cleaned_tags) <= 10
        assert not any('script' in tag.lower() for tag in cleaned_tags)
        assert 'tech' in cleaned_tags
        assert 'news' in cleaned_tags
    
    def test_valid_author_validation(self):
        """Test validation of valid author data"""
        author_data = {
            'name': 'John Doe',
            'slug': 'john-doe',
            'title': 'Tech Writer',
            'bio': 'Experienced technology writer with 10 years of experience.',
            'email': 'john@example.com',
            'twitter': 'https://twitter.com/johndoe',
            'linkedin': 'https://linkedin.com/in/johndoe'
        }
        
        result = self.validator.validate_author(author_data)
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_missing_required_author_fields(self):
        """Test validation with missing required author fields"""
        incomplete_data = {
            'bio': 'Just a bio, missing name and slug'
        }
        
        result = self.validator.validate_author(incomplete_data)
        assert not result.is_valid
        assert len(result.errors) >= 2  # Missing name and slug
    
    def test_author_email_validation(self):
        """Test author email validation"""
        test_emails = [
            ('valid@example.com', True),
            ('invalid.email', False),
            ('user@domain', False),
            ('', True),  # Empty is OK (not required)
        ]
        
        base_data = {
            'name': 'Test Author',
            'slug': 'test-author'
        }
        
        for email, should_be_valid in test_emails:
            author_data = base_data.copy()
            if email:  # Don't add empty email
                author_data['email'] = email
            
            result = self.validator.validate_author(author_data)
            email_errors = [e for e in result.errors if 'email' in e.lower()]
            
            if should_be_valid:
                assert len(email_errors) == 0, f"Valid email {email} was rejected"
            else:
                assert len(email_errors) > 0, f"Invalid email {email} was accepted"
    
    def test_author_social_links_validation(self):
        """Test author social links validation"""
        author_data = {
            'name': 'Test Author',
            'slug': 'test-author',
            'twitter': 'javascript:alert("xss")',  # Dangerous
            'linkedin': 'https://linkedin.com/in/valid',  # Valid
            'instagram': 'not-a-url',  # Invalid
        }
        
        result = self.validator.validate_author(author_data)
        
        # Should remove dangerous Twitter link
        assert result.cleaned_content['twitter'] == ''
        # Should keep valid LinkedIn
        assert 'linkedin.com' in result.cleaned_content['linkedin']
        # Should have errors for invalid URLs
        assert any('url' in error.lower() for error in result.errors)
    
    def test_author_xss_in_bio(self):
        """Test XSS prevention in author bio"""
        author_data = {
            'name': 'Test Author',
            'slug': 'test-author',
            'bio': 'Safe bio content <script>alert("XSS")</script> more bio'
        }
        
        result = self.validator.validate_author(author_data)
        assert not result.is_valid
        assert 'script' not in result.cleaned_content['bio'].lower()
        assert any('dangerous content' in error.lower() for error in result.errors)


class TestAdvancedXSSPrevention:
    """Advanced XSS prevention tests"""
    
    def setup_method(self):
        """Setup test instance"""
        self.sanitizer = ContentSanitizer()
    
    def test_encoded_script_attacks(self):
        """Test prevention of encoded script attacks"""
        encoded_attacks = [
            '&lt;script&gt;alert("XSS")&lt;/script&gt;',
            '%3Cscript%3Ealert("XSS")%3C/script%3E',
            '&#60;script&#62;alert("XSS")&#60;/script&#62;',
        ]
        
        for attack in encoded_attacks:
            result = self.sanitizer.sanitize_content(attack)
            # Even encoded, should be safe after our sanitization
            assert 'alert' not in result.cleaned_content
    
    def test_svg_xss_attacks(self):
        """Test prevention of SVG-based XSS"""
        svg_attacks = [
            '<svg onload="alert(1)">',
            '<svg><script>alert("XSS")</script></svg>',
        ]
        
        for attack in svg_attacks:
            result = self.sanitizer.sanitize_content(attack)
            assert not result.is_valid
            assert 'onload' not in result.cleaned_content
            assert 'script' not in result.cleaned_content.lower()
    
    def test_css_injection_attacks(self):
        """Test prevention of CSS injection attacks"""
        css_attacks = [
            '<style>body { background: url("javascript:alert(1)"); }</style>',
            '<div style="background:url(javascript:alert(1))">',
        ]
        
        for attack in css_attacks:
            result = self.sanitizer.sanitize_content(attack)
            assert not result.is_valid
            assert 'javascript:' not in result.cleaned_content
    
    def test_polyglot_attacks(self):
        """Test prevention of polyglot attacks"""
        polyglot = 'jaVasCript:/*-/*`/*\\`/*\'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\\x3csVg/<sVg/oNloAd=alert()//'
        
        result = self.sanitizer.sanitize_content(polyglot)
        assert not result.is_valid
        assert 'javascript:' not in result.cleaned_content.lower()
        assert 'onclick' not in result.cleaned_content.lower()
        assert 'onload' not in result.cleaned_content.lower()
        assert 'alert' not in result.cleaned_content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])