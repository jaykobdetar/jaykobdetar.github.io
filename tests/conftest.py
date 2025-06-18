"""
Pytest configuration and fixtures for Influencer News CMS tests
Provides shared test setup, teardown, and utilities
"""

import os
import sys
import tempfile
import shutil
import sqlite3
from pathlib import Path
from typing import Generator
import pytest

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from src.database.db_manager import DatabaseManager
from src.models.author import Author
from src.models.category import Category
from src.models.article import Article
from src.models.trending import TrendingTopic
from src.utils.config import config

@pytest.fixture(scope="session")
def test_config():
    """Configure test settings"""
    # Set test-specific configuration
    config.set('database.path', 'test_data/test_cms.db')
    config.set('paths.content_dir', 'test_data/content')
    config.set('paths.integrated_dir', 'test_data/integrated')
    config.set('paths.assets_dir', 'test_data/assets')
    config.set('logging.level', 'DEBUG')
    config.set('logging.file', 'test_data/logs/test.log')
    
    # Create test directories
    test_dirs = [
        'test_data',
        'test_data/content',
        'test_data/integrated',
        'test_data/assets',
        'test_data/logs'
    ]
    
    for dir_path in test_dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    return config

@pytest.fixture
def temp_database(test_config):
    """Create a temporary test database"""
    db_path = Path(test_config.get('database.path'))
    
    # Remove existing test database
    if db_path.exists():
        db_path.unlink()
    
    # Create fresh database
    db = DatabaseManager()
    
    yield db
    
    # Cleanup
    if db_path.exists():
        db_path.unlink()

@pytest.fixture
def sample_author_data():
    """Sample author data for testing"""
    return {
        'name': 'John Doe',
        'slug': 'john-doe',
        'title': 'Tech Journalist',
        'bio': 'Experienced technology journalist with 10 years in the industry',
        'email': 'john.doe@example.com',
        'location': 'San Francisco, CA',
        'expertise': 'AI, Machine Learning, Tech Trends',
        'twitter': '@johndoe',
        'linkedin': 'linkedin.com/in/johndoe'
    }

@pytest.fixture
def sample_category_data():
    """Sample category data for testing"""
    return {
        'name': 'Technology',
        'slug': 'technology',
        'description': 'Latest in tech and innovation',
        'icon': '💻',
        'color': 'blue'
    }

@pytest.fixture
def sample_article_data():
    """Sample article data for testing"""
    return {
        'title': 'The Future of AI in Content Creation',
        'slug': 'future-ai-content-creation',
        'subtitle': 'How artificial intelligence is reshaping the creator economy',
        'content': 'This is a comprehensive article about AI in content creation. ' * 50,
        'author_id': 1,
        'category_id': 1,
        'publication_date': '2024-12-10',
        'read_time': 5,
        'meta_description': 'Exploring how AI is transforming content creation',
        'tags': ['AI', 'Content Creation', 'Technology']
    }

@pytest.fixture
def sample_trending_data():
    """Sample trending topic data for testing"""
    return {
        'title': 'AI Content Revolution',
        'slug': 'ai-content-revolution',
        'description': 'The rise of AI-powered content creation tools',
        'icon': '🤖',
        'heat_score': 85,
        'category_id': 1
    }

@pytest.fixture
def populated_database(temp_database, sample_author_data, sample_category_data, 
                      sample_article_data, sample_trending_data):
    """Database populated with sample data"""
    db = temp_database
    
    # Create author
    author = Author.create(**sample_author_data)
    
    # Create category
    category = Category.create(**sample_category_data)
    
    # Update article data with correct IDs
    article_data = sample_article_data.copy()
    article_data['author_id'] = author.id
    article_data['category_id'] = category.id
    
    # Create article
    article = Article.create(**article_data)
    
    # Update trending data with correct category ID
    trending_data = sample_trending_data.copy()
    trending_data['category_id'] = category.id
    
    # Create trending topic
    trending = TrendingTopic.create(**trending_data)
    
    return {
        'db': db,
        'author': author,
        'category': category,
        'article': article,
        'trending': trending
    }

@pytest.fixture
def temp_content_files(test_config):
    """Create temporary content files for testing"""
    content_dir = Path(test_config.get('paths.content_dir'))
    
    # Create author file
    author_file = content_dir / 'authors' / 'test-author.txt'
    author_file.parent.mkdir(parents=True, exist_ok=True)
    author_file.write_text("""Name: Test Author
Title: Test Journalist
Bio: A test author for unit testing
Email: test@example.com
Location: Test City
Expertise: Testing, QA
Twitter: @testauthor
LinkedIn: linkedin.com/in/testauthor

---

Test author bio content goes here.
""")
    
    # Create category file
    category_file = content_dir / 'categories' / 'test-category.txt'
    category_file.parent.mkdir(parents=True, exist_ok=True)
    category_file.write_text("""Name: Test Category
Description: A test category for unit testing
Icon: 🧪
Color: green

---

Test category description goes here.
""")
    
    # Create article file
    article_file = content_dir / 'articles' / 'test-article.txt'
    article_file.parent.mkdir(parents=True, exist_ok=True)
    article_file.write_text("""Title: Test Article
Subtitle: A test article for unit testing
Author: Test Author
Category: Test Category
Publication Date: 2024-12-10
Read Time: 3
Tags: testing, qa, unit-tests

---

This is a test article content for unit testing purposes.
It contains multiple paragraphs to test content processing.

The content should be properly parsed and validated.
""")
    
    yield {
        'author_file': author_file,
        'category_file': category_file,
        'article_file': article_file
    }
    
    # Cleanup
    if content_dir.exists():
        shutil.rmtree(content_dir)

@pytest.fixture
def mock_image_url():
    """Mock image URL for testing"""
    return "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=300"

def pytest_configure(config):
    """Configure pytest settings"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        # Add 'unit' marker to all tests in test_unit_* files
        if "test_unit_" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        
        # Add 'integration' marker to all tests in test_integration_* files
        if "test_integration_" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add 'slow' marker to tests that might be slow
        if any(keyword in item.name.lower() for keyword in ['backup', 'restore', 'large', 'performance']):
            item.add_marker(pytest.mark.slow)

@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Automatically cleanup test data after each test"""
    yield
    
    # Cleanup test directories
    test_dirs = ['test_data']
    for dir_path in test_dirs:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
            except:
                pass  # Ignore cleanup errors