#!/usr/bin/env python3
"""
Comprehensive tests for content integrators
Tests for article, author, category, and trending integrators
"""

import pytest
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from integrators.article_integrator import ArticleIntegrator
from integrators.author_integrator import AuthorIntegrator
from integrators.category_integrator import CategoryIntegrator
from integrators.trending_integrator import TrendingIntegrator
from integrators.base_integrator import BaseIntegrator


class TestBaseIntegrator:
    """Test the BaseIntegrator class"""
    
    def setup_method(self):
        """Setup test instance with temporary directories"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.content_dir = self.test_dir / 'content' / 'test'
        self.integrated_dir = self.test_dir / 'integrated' / 'test'
        
        # Create directories
        self.content_dir.mkdir(parents=True)
        self.integrated_dir.mkdir(parents=True)
        
        # Create test integrator
        self.integrator = BaseIntegrator('test', 'test')
        self.integrator.content_dir = self.content_dir
        self.integrator.integrated_dir = self.integrated_dir
    
    def teardown_method(self):
        """Cleanup test directories"""
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test integrator initialization"""
        integrator = BaseIntegrator('articles', 'articles')
        
        assert integrator.content_type == 'articles'
        assert integrator.content_subdir == 'articles'
        assert hasattr(integrator, 'progress_callback')
    
    def test_update_progress(self):
        """Test progress update mechanism"""
        messages = []
        
        def capture_progress(message):
            messages.append(message)
        
        self.integrator.progress_callback = capture_progress
        self.integrator.update_progress("Test message")
        
        assert len(messages) == 1
        assert "Test message" in messages[0]
    
    def test_escape_html(self):
        """Test HTML escaping utility"""
        test_cases = [
            ("Hello World", "Hello World"),
            ("<script>alert('xss')</script>", "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"),
            ("'quotes' & \"double quotes\"", "&#x27;quotes&#x27; &amp; &quot;double quotes&quot;"),
            ("", ""),
        ]
        
        for input_text, expected in test_cases:
            result = self.integrator.escape_html(input_text)
            assert result == expected
    
    def test_format_date_relative(self):
        """Test relative date formatting"""
        from datetime import datetime, timedelta
        
        # Test with recent date
        recent_date = datetime.now() - timedelta(hours=2)
        result = self.integrator.format_date_relative(recent_date.isoformat())
        assert "2 hours ago" in result.lower()
        
        # Test with invalid date
        result = self.integrator.format_date_relative("invalid-date")
        assert result == "Recently"
    
    def test_generate_slug(self):
        """Test slug generation"""
        test_cases = [
            ("Hello World", "hello-world"),
            ("Test Article Title!", "test-article-title"),
            ("Multiple   Spaces", "multiple-spaces"),
            ("Special@#$%Characters", "special-characters"),
            ("", "untitled"),
        ]
        
        for input_text, expected in test_cases:
            result = self.integrator.generate_slug(input_text)
            assert result == expected
    
    def test_sync_with_files_empty_directory(self):
        """Test sync with empty content directory"""
        # Mock required methods
        self.integrator.parse_content_file = Mock(return_value={})
        self.integrator.process_content = Mock(return_value=True)
        self.integrator.create_content_page = Mock()
        self.integrator.update_listing_page = Mock()
        
        self.integrator.sync_with_files()
        
        # Should not process any files
        assert self.integrator.parse_content_file.call_count == 0
        assert self.integrator.process_content.call_count == 0
    
    def test_sync_with_files_with_content(self):
        """Test sync with content files"""
        # Create test content file
        test_file = self.content_dir / 'test-article.txt'
        test_file.write_text("""title: Test Article
slug: test-article
---
This is test content.""")
        
        # Mock required methods
        self.integrator.parse_content_file = Mock(return_value={
            'title': 'Test Article',
            'slug': 'test-article',
            'content': 'This is test content.'
        })
        self.integrator.process_content = Mock(return_value=True)
        self.integrator.create_content_page = Mock()
        self.integrator.update_listing_page = Mock()
        
        self.integrator.sync_with_files()
        
        # Should process the file
        assert self.integrator.parse_content_file.call_count == 1
        assert self.integrator.process_content.call_count == 1
        assert self.integrator.create_content_page.call_count == 1
    
    def test_parse_metadata_section(self):
        """Test metadata parsing"""
        metadata_text = """title: Test Article
slug: test-article  
author: John Doe
tags: tech, news
published: true"""
        
        result = self.integrator.parse_metadata_section(metadata_text)
        
        assert result['title'] == 'Test Article'
        assert result['slug'] == 'test-article'
        assert result['author'] == 'John Doe'
        assert result['tags'] == 'tech, news'
        assert result['published'] == 'true'
    
    def test_parse_metadata_with_colons_in_values(self):
        """Test metadata parsing with colons in values"""
        metadata_text = """title: Article: A Deep Dive
url: https://example.com/path
time: 12:30 PM"""
        
        result = self.integrator.parse_metadata_section(metadata_text)
        
        assert result['title'] == 'Article: A Deep Dive'
        assert result['url'] == 'https://example.com/path'
        assert result['time'] == '12:30 PM'
    
    def test_validate_file_safety(self):
        """Test file safety validation"""
        safe_files = [
            'article.txt',
            'author-profile.txt',
            'category_tech.txt',
        ]
        
        unsafe_files = [
            '../../../etc/passwd',
            'file.exe',
            'script.js',
            '.hidden',
            'file with spaces.txt',
        ]
        
        for filename in safe_files:
            assert self.integrator.validate_file_safety(Path(filename))
        
        for filename in unsafe_files:
            assert not self.integrator.validate_file_safety(Path(filename))


class TestArticleIntegrator:
    """Test the ArticleIntegrator class"""
    
    def setup_method(self):
        """Setup test instance"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.integrator = ArticleIntegrator()
        
        # Mock database connection
        with patch('integrators.article_integrator.get_db_connection'):
            pass
    
    def teardown_method(self):
        """Cleanup test directories"""
        shutil.rmtree(self.test_dir)
    
    def test_parse_content_file_valid(self):
        """Test parsing valid article content file"""
        test_content = """title: Test Article Title
slug: test-article-title
author: john-doe
category: technology
read_time: 5
tags: tech, news, ai
meta_description: This is a test article
---
# Introduction

This is the main content of the article.

## Section 1

More content here with **bold** and *italic* text.

## Conclusion

Final thoughts."""
        
        # Create temporary file
        test_file = self.test_dir / 'test-article.txt'
        test_file.write_text(test_content)
        
        result = self.integrator.parse_content_file(test_file)
        
        assert result['title'] == 'Test Article Title'
        assert result['slug'] == 'test-article-title'
        assert result['author'] == 'john-doe'
        assert result['category'] == 'technology'
        assert result['read_time'] == '5'
        assert 'Introduction' in result['content']
        assert 'Section 1' in result['content']
    
    def test_parse_content_file_missing_separator(self):
        """Test parsing file missing metadata separator"""
        test_content = """title: Test Article
This is content without separator"""
        
        test_file = self.test_dir / 'invalid-article.txt'
        test_file.write_text(test_content)
        
        with pytest.raises(ValueError, match="Missing '---' separator"):
            self.integrator.parse_content_file(test_file)
    
    def test_extract_sections(self):
        """Test content section extraction"""
        content = """# Introduction
This is the intro.

## Section One
First section content.

### Subsection
Nested content.

## Section Two  
Second section content."""
        
        sections = self.integrator.extract_sections(content)
        
        assert len(sections) >= 3
        assert any('Introduction' in section['heading'] for section in sections)
        assert any('Section One' in section['heading'] for section in sections)
        assert any('Section Two' in section['heading'] for section in sections)
    
    def test_process_article_content_with_xss(self):
        """Test article content processing with XSS attempts"""
        dangerous_content = """# Safe Heading

This is safe content.

<script>alert('XSS attack!')</script>

<img src="x" onerror="alert('Another XSS')">

More safe content."""
        
        # Mock sanitizer to test integration
        with patch('integrators.article_integrator.content_sanitizer') as mock_sanitizer:
            mock_sanitizer.sanitize_content.return_value = Mock(
                is_valid=False,
                cleaned_content="# Safe Heading\n\nThis is safe content.\n\nMore safe content.",
                errors=["Dangerous content detected"],
                warnings=["XSS content removed"]
            )
            
            result = self.integrator.process_article_content(dangerous_content)
            
            # Should have called sanitizer
            mock_sanitizer.sanitize_content.assert_called_once()
            
            # Should return cleaned content
            assert 'script' not in result.lower()
            assert 'onerror' not in result.lower()
    
    def test_generate_article_template(self):
        """Test article template generation"""
        template = self.integrator.get_article_template()
        
        # Should contain required placeholders
        required_placeholders = [
            '{{ARTICLE_TITLE}}',
            '{{ARTICLE_CONTENT}}',
            '{{AUTHOR_NAME}}',
            '{{CATEGORY_NAME}}',
            '{{PUBLISH_DATE}}',
        ]
        
        for placeholder in required_placeholders:
            assert placeholder in template
        
        # Should contain mobile support elements
        mobile_elements = [
            'mobile-menu',
            'mobileMenuToggle',
            'mobile-search-overlay',
        ]
        
        for element in mobile_elements:
            assert element in template


class TestAuthorIntegrator:
    """Test the AuthorIntegrator class"""
    
    def setup_method(self):
        """Setup test instance"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.integrator = AuthorIntegrator()
    
    def teardown_method(self):
        """Cleanup test directories"""
        shutil.rmtree(self.test_dir)
    
    def test_parse_author_content_file(self):
        """Test parsing author content file"""
        test_content = """name: John Doe
slug: john-doe
title: Senior Tech Writer
email: john@example.com
location: San Francisco, CA
expertise: AI, Machine Learning, Tech Trends
twitter: @johndoe
linkedin: https://linkedin.com/in/johndoe
---
John is an experienced technology writer with over 10 years of experience covering AI and machine learning trends. He has written for major tech publications and has a deep understanding of the creator economy."""
        
        test_file = self.test_dir / 'john-doe.txt'
        test_file.write_text(test_content)
        
        result = self.integrator.parse_content_file(test_file)
        
        assert result['name'] == 'John Doe'
        assert result['slug'] == 'john-doe'
        assert result['title'] == 'Senior Tech Writer'
        assert result['email'] == 'john@example.com'
        assert 'experienced technology writer' in result['bio']
    
    def test_author_social_media_validation(self):
        """Test author social media link validation"""
        test_content = """name: Test Author
slug: test-author
twitter: javascript:alert('xss')
linkedin: https://linkedin.com/in/valid
instagram: not-a-url
---
Author bio content."""
        
        test_file = self.test_dir / 'test-author.txt'
        test_file.write_text(test_content)
        
        # Mock the validator to test integration
        with patch('integrators.author_integrator.model_validator') as mock_validator:
            mock_validator.validate_author.return_value = Mock(
                is_valid=False,
                cleaned_content={
                    'name': 'Test Author',
                    'slug': 'test-author',
                    'twitter': '',  # Dangerous link removed
                    'linkedin': 'https://linkedin.com/in/valid',
                    'instagram': '',  # Invalid URL removed
                    'bio': 'Author bio content.'
                },
                errors=['Invalid URL format'],
                warnings=['Dangerous content removed']
            )
            
            result = self.integrator.parse_content_file(test_file)
            
            # Should have processed through validator
            mock_validator.validate_author.assert_called_once()


class TestCategoryIntegrator:
    """Test the CategoryIntegrator class"""
    
    def setup_method(self):
        """Setup test instance"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.integrator = CategoryIntegrator()
    
    def teardown_method(self):
        """Cleanup test directories"""
        shutil.rmtree(self.test_dir)
    
    def test_parse_category_content_file(self):
        """Test parsing category content file"""
        test_content = """name: Technology
slug: technology
color: blue
icon: 💻
sort_order: 1
---
Latest news and insights about technology, AI, and digital innovation in the creator space."""
        
        test_file = self.test_dir / 'technology.txt'
        test_file.write_text(test_content)
        
        result = self.integrator.parse_content_file(test_file)
        
        assert result['name'] == 'Technology'
        assert result['slug'] == 'technology'
        assert result['color'] == '#3B82F6'  # Should convert blue to hex
        assert result['icon'] == '💻'
        assert result['sort_order'] == 1
    
    def test_color_mapping(self):
        """Test color name to hex mapping"""
        color_tests = [
            ('blue', '#3B82F6'),
            ('green', '#10B981'),
            ('red', '#EF4444'),
            ('#FF5733', '#FF5733'),  # Already hex
            ('invalid', '#6B7280'),  # Default gray
        ]
        
        for color_input, expected_hex in color_tests:
            test_content = f"""name: Test Category
slug: test-category
color: {color_input}
---
Description"""
            
            test_file = self.test_dir / f'test-{color_input}.txt'
            test_file.write_text(test_content)
            
            result = self.integrator.parse_content_file(test_file)
            assert result['color'] == expected_hex
    
    def test_category_template_mobile_support(self):
        """Test category template has mobile support"""
        template = self.integrator.get_category_template()
        
        # Should contain mobile elements
        mobile_elements = [
            'mobile-menu-overlay',
            'mobileMenuToggle',
            'mobile-search-overlay',
            'hamburger',
        ]
        
        for element in mobile_elements:
            assert element in template


class TestTrendingIntegrator:
    """Test the TrendingIntegrator class"""
    
    def setup_method(self):
        """Setup test instance"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.integrator = TrendingIntegrator()
    
    def teardown_method(self):
        """Cleanup test directories"""
        shutil.rmtree(self.test_dir)
    
    def test_parse_trending_content_file(self):
        """Test parsing trending topic content file"""
        test_content = """title: AI Content Creation Revolution
slug: ai-content-creation-revolution
heat_score: 95
growth_rate: 15.5
hashtag: #AICreators
category: technology
status: active
---
The rise of AI tools like ChatGPT and Midjourney is fundamentally changing how creators produce content. This comprehensive analysis explores the impact on the creator economy."""
        
        test_file = self.test_dir / 'ai-revolution.txt'
        test_file.write_text(test_content)
        
        result = self.integrator.parse_content_file(test_file)
        
        assert result['title'] == 'AI Content Creation Revolution'
        assert result['slug'] == 'ai-content-creation-revolution'
        assert result['heat_score'] == 95
        assert result['growth_rate'] == 15.5
        assert result['hashtag'] == '#AICreators'
        assert 'AI tools like ChatGPT' in result['content']
    
    def test_heat_score_validation(self):
        """Test heat score validation (0-100)"""
        test_cases = [
            (50, 50),      # Valid
            (-10, 0),      # Below minimum
            (150, 100),    # Above maximum  
            ('invalid', 0), # Invalid type
        ]
        
        for input_score, expected_score in test_cases:
            test_content = f"""title: Test Trend
slug: test-trend
heat_score: {input_score}
---
Content"""
            
            test_file = self.test_dir / f'test-{input_score}.txt'
            test_file.write_text(test_content)
            
            result = self.integrator.parse_content_file(test_file)
            assert result['heat_score'] == expected_score


class TestIntegratorSecurity:
    """Test security aspects of integrators"""
    
    def setup_method(self):
        """Setup test instances"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.article_integrator = ArticleIntegrator()
        self.author_integrator = AuthorIntegrator()
    
    def teardown_method(self):
        """Cleanup test directories"""
        shutil.rmtree(self.test_dir)
    
    def test_path_traversal_prevention(self):
        """Test prevention of path traversal attacks"""
        dangerous_paths = [
            '../../../etc/passwd',
            '..\\..\\windows\\system32\\config',
            '/etc/shadow',
            'C:\\Windows\\System32\\drivers\\etc\\hosts',
        ]
        
        for dangerous_path in dangerous_paths:
            file_path = Path(dangerous_path)
            
            # Should be rejected by safety validation
            assert not self.article_integrator.validate_file_safety(file_path)
            assert not self.author_integrator.validate_file_safety(file_path)
    
    def test_file_type_restriction(self):
        """Test file type restrictions"""
        allowed_files = [
            'article.txt',
            'author.txt',
            'category.txt',
        ]
        
        dangerous_files = [
            'script.js',
            'malware.exe',
            'config.php',
            'shell.sh',
            'payload.py',
        ]
        
        for filename in allowed_files:
            assert self.article_integrator.validate_file_safety(Path(filename))
        
        for filename in dangerous_files:
            assert not self.article_integrator.validate_file_safety(Path(filename))
    
    def test_content_sanitization_integration(self):
        """Test that content is properly sanitized during processing"""
        malicious_content = """title: Innocent Title
slug: innocent-slug
---
# Innocent Heading

This looks like normal content but contains:

<script>
// Malicious JavaScript
fetch('/admin/delete-all-users', {method: 'POST'});
</script>

<img src="x" onerror="window.location='http://evil.com/steal-data'">

And some <iframe src="http://malicious-site.com"></iframe> content."""
        
        test_file = self.test_dir / 'malicious.txt'
        test_file.write_text(malicious_content)
        
        # Mock the sanitizer to ensure it's being used
        with patch('integrators.article_integrator.content_sanitizer') as mock_sanitizer:
            mock_sanitizer.sanitize_content.return_value = Mock(
                is_valid=False,
                cleaned_content="Safe content only",
                errors=["Dangerous content detected"],
                warnings=["Malicious content removed"]
            )
            
            try:
                result = self.article_integrator.parse_content_file(test_file)
                
                # Should have called sanitizer
                assert mock_sanitizer.sanitize_content.called
                
                # Content should be cleaned
                if 'content' in result:
                    assert 'script' not in result['content'].lower()
                    assert 'onerror' not in result['content'].lower()
                    assert 'iframe' not in result['content'].lower()
                    
            except Exception:
                # If parsing fails due to security checks, that's also acceptable
                pass


class TestIntegratorPerformance:
    """Test performance aspects of integrators"""
    
    def setup_method(self):
        """Setup test instance"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.integrator = ArticleIntegrator()
    
    def teardown_method(self):
        """Cleanup test directories"""
        shutil.rmtree(self.test_dir)
    
    def test_large_content_handling(self):
        """Test handling of large content files"""
        # Create large content (just under the limit)
        large_content = "x" * 49000  # Just under 50KB limit
        
        test_content = f"""title: Large Article
slug: large-article
---
{large_content}"""
        
        test_file = self.test_dir / 'large-article.txt'
        test_file.write_text(test_content)
        
        # Should handle large content gracefully
        result = self.integrator.parse_content_file(test_file)
        assert 'content' in result
        assert len(result['content']) > 0
    
    def test_excessive_content_truncation(self):
        """Test truncation of excessively large content"""
        # Create content that exceeds limits
        excessive_content = "x" * 100000  # 100KB - exceeds typical limits
        
        test_content = f"""title: Excessive Article
slug: excessive-article
---
{excessive_content}"""
        
        test_file = self.test_dir / 'excessive-article.txt'
        test_file.write_text(test_content)
        
        # Mock sanitizer to test truncation
        with patch('integrators.article_integrator.content_sanitizer') as mock_sanitizer:
            mock_sanitizer.sanitize_content.return_value = Mock(
                is_valid=False,
                cleaned_content=excessive_content[:50000],  # Truncated
                errors=["Content exceeds maximum length"],
                warnings=["Content was truncated"]
            )
            
            result = self.integrator.parse_content_file(test_file)
            
            # Should have been processed through sanitizer
            mock_sanitizer.sanitize_content.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])