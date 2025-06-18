"""
Unit tests for CMS models
Tests individual model classes and their methods
"""

import pytest
from datetime import datetime
from src.models.author import Author
from src.models.category import Category
from src.models.article import Article
from src.models.trending import TrendingTopic


@pytest.mark.unit
class TestAuthorModel:
    """Test Author model functionality"""
    
    def test_author_creation(self, sample_author_data):
        """Test creating an author instance"""
        author = Author(**sample_author_data)
        
        assert author.name == sample_author_data['name']
        assert author.slug == sample_author_data['slug']
        assert author.email == sample_author_data['email']
        assert author.title == sample_author_data['title']
        assert author.bio == sample_author_data['bio']
    
    def test_author_to_dict(self, sample_author_data):
        """Test converting author to dictionary"""
        author = Author(**sample_author_data)
        author_dict = author.to_dict()
        
        assert author_dict['name'] == sample_author_data['name']
        assert author_dict['slug'] == sample_author_data['slug']
        assert author_dict['email'] == sample_author_data['email']
    
    def test_author_from_dict(self, sample_author_data):
        """Test creating author from dictionary"""
        author = Author.from_dict(sample_author_data)
        
        assert isinstance(author, Author)
        assert author.name == sample_author_data['name']
        assert author.slug == sample_author_data['slug']


@pytest.mark.unit
class TestCategoryModel:
    """Test Category model functionality"""
    
    def test_category_creation(self, sample_category_data):
        """Test creating a category instance"""
        category = Category(**sample_category_data)
        
        assert category.name == sample_category_data['name']
        assert category.slug == sample_category_data['slug']
        assert category.description == sample_category_data['description']
        assert category.icon == sample_category_data['icon']
        assert category.color == sample_category_data['color']
    
    def test_category_to_dict(self, sample_category_data):
        """Test converting category to dictionary"""
        category = Category(**sample_category_data)
        category_dict = category.to_dict()
        
        assert category_dict['name'] == sample_category_data['name']
        assert category_dict['slug'] == sample_category_data['slug']
        assert category_dict['description'] == sample_category_data['description']


@pytest.mark.unit
class TestArticleModel:
    """Test Article model functionality"""
    
    def test_article_creation(self, sample_article_data):
        """Test creating an article instance"""
        article = Article(**sample_article_data)
        
        assert article.title == sample_article_data['title']
        assert article.slug == sample_article_data['slug']
        assert article.subtitle == sample_article_data['subtitle']
        assert article.content == sample_article_data['content']
        assert article.author_id == sample_article_data['author_id']
        assert article.category_id == sample_article_data['category_id']
    
    def test_article_tags_parsing(self):
        """Test article tags parsing from JSON string"""
        # Test with JSON string
        article_data = {
            'title': 'Test Article',
            'tags': '["AI", "Technology", "Innovation"]'
        }
        article = Article(**article_data)
        assert article.tags == ["AI", "Technology", "Innovation"]
        
        # Test with list
        article_data['tags'] = ["AI", "Technology"]
        article = Article(**article_data)
        assert article.tags == ["AI", "Technology"]
        
        # Test with empty string
        article_data['tags'] = ""
        article = Article(**article_data)
        assert article.tags == []
    
    def test_article_to_dict(self, sample_article_data):
        """Test converting article to dictionary"""
        article = Article(**sample_article_data)
        article_dict = article.to_dict()
        
        assert article_dict['title'] == sample_article_data['title']
        assert article_dict['slug'] == sample_article_data['slug']
        assert article_dict['tags'] == sample_article_data['tags']


@pytest.mark.unit
class TestTrendingTopicModel:
    """Test TrendingTopic model functionality"""
    
    def test_trending_topic_creation(self, sample_trending_data):
        """Test creating a trending topic instance"""
        trending = TrendingTopic(**sample_trending_data)
        
        assert trending.title == sample_trending_data['title']
        assert trending.slug == sample_trending_data['slug']
        assert trending.description == sample_trending_data['description']
        assert trending.icon == sample_trending_data['icon']
        assert trending.heat_score == sample_trending_data['heat_score']
    
    def test_trending_topic_to_dict(self, sample_trending_data):
        """Test converting trending topic to dictionary"""
        trending = TrendingTopic(**sample_trending_data)
        trending_dict = trending.to_dict()
        
        assert trending_dict['title'] == sample_trending_data['title']
        assert trending_dict['heat_score'] == sample_trending_data['heat_score']


@pytest.mark.unit
class TestBaseModel:
    """Test BaseModel functionality"""
    
    def test_base_model_initialization(self):
        """Test base model can be initialized with kwargs"""
        from src.models.base import BaseModel
        
        data = {
            'id': 1,
            'created_at': datetime.now(),
            'custom_field': 'test_value'
        }
        
        model = BaseModel(**data)
        assert model.id == 1
        assert model.custom_field == 'test_value'
        assert isinstance(model.created_at, datetime)
    
    def test_base_model_to_dict_with_datetime(self):
        """Test base model to_dict handles datetime objects"""
        from src.models.base import BaseModel
        
        now = datetime.now()
        model = BaseModel(id=1, created_at=now, name='test')
        
        result = model.to_dict()
        assert result['id'] == 1
        assert result['name'] == 'test'
        assert result['created_at'] == now.isoformat()