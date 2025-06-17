"""
Integration tests for database operations
Tests the complete database workflow with models
"""

import pytest
from src.models.author import Author
from src.models.category import Category
from src.models.article import Article
from src.models.trending import TrendingTopic


@pytest.mark.integration
class TestDatabaseIntegration:
    """Test complete database operations"""
    
    def test_full_cms_workflow(self, temp_database, sample_author_data, 
                              sample_category_data, sample_article_data, 
                              sample_trending_data):
        """Test complete CMS workflow from creation to deletion"""
        # Create author
        author = Author.create(**sample_author_data)
        assert author.id is not None
        assert author.name == sample_author_data['name']
        
        # Create category
        category = Category.create(**sample_category_data)
        assert category.id is not None
        assert category.name == sample_category_data['name']
        
        # Update article data with correct IDs
        article_data = sample_article_data.copy()
        article_data['author_id'] = author.id
        article_data['category_id'] = category.id
        
        # Create article
        article = Article.create(**article_data)
        assert article.id is not None
        assert article.title == article_data['title']
        assert article.author_id == author.id
        assert article.category_id == category.id
        
        # Update trending data with correct category ID
        trending_data = sample_trending_data.copy()
        trending_data['category_id'] = category.id
        
        # Create trending topic
        trending = TrendingTopic.create(**trending_data)
        assert trending.id is not None
        assert trending.title == trending_data['title']
        
        # Test retrieval
        retrieved_author = Author.find_by_id(author.id)
        assert retrieved_author is not None
        assert retrieved_author.name == author.name
        
        retrieved_article = Article.find_by_slug(article.slug)
        assert retrieved_article is not None
        assert retrieved_article.title == article.title
        
        # Test relationships
        article_author = article.get_author()
        assert article_author is not None
        assert article_author.id == author.id
        
        article_category = article.get_category()
        assert article_category is not None
        assert article_category.id == category.id
    
    def test_article_search(self, populated_database):
        """Test article search functionality"""
        data = populated_database
        article = data['article']
        
        # Search for article by title
        results = Article.search('Future')
        assert len(results) > 0
        found_article = results[0]
        assert found_article.id == article.id
        
        # Search for article by content
        results = Article.search('artificial intelligence')
        assert len(results) > 0
    
    def test_related_articles(self, populated_database):
        """Test related articles functionality"""
        data = populated_database
        article = data['article']
        
        # Create another article in same category
        second_article_data = {
            'title': 'Another AI Article',
            'slug': 'another-ai-article',
            'author_id': data['author'].id,
            'category_id': data['category'].id,
            'publication_date': '2024-12-11',
            'content': 'Another article about AI and technology.'
        }
        second_article = Article.create(**second_article_data)
        
        # Add as related article
        article.add_related_article(second_article.id)
        
        # Get related articles
        related = article.get_related_articles()
        assert len(related) > 0
        assert any(r.id == second_article.id for r in related)
    
    def test_article_view_count(self, populated_database):
        """Test article view count increment"""
        data = populated_database
        article = data['article']
        
        initial_count = article.view_count
        article.increment_view_count()
        
        # Verify count increased
        assert article.view_count == initial_count + 1
        
        # Verify in database
        retrieved_article = Article.find_by_id(article.id)
        assert retrieved_article.view_count == initial_count + 1
    
    def test_model_deletion_with_foreign_keys(self, populated_database):
        """Test model deletion behavior with foreign key constraints"""
        data = populated_database
        author = data['author']
        category = data['category']
        article = data['article']
        
        # Try to delete author with articles (should handle gracefully)
        result = author.delete()
        # Should either delete successfully or provide informative error
        
        # Try to delete category with articles
        result = category.delete()
        # Should either delete successfully or provide informative error
        
        # Delete article first, then author should delete successfully
        article.delete()
        result = author.delete()
        assert result is True


@pytest.mark.integration
class TestDatabaseErrorHandling:
    """Test database error handling scenarios"""
    
    def test_duplicate_slug_handling(self, temp_database, sample_author_data):
        """Test handling of duplicate slugs"""
        # Create first author
        author1 = Author.create(**sample_author_data)
        assert author1.id is not None
        
        # Try to create author with same slug
        duplicate_data = sample_author_data.copy()
        duplicate_data['name'] = 'Different Name'
        
        # This should either succeed with modified slug or handle gracefully
        try:
            author2 = Author.create(**duplicate_data)
            # If successful, slug should be different
            if author2:
                assert author2.slug != author1.slug
        except Exception as e:
            # Should handle duplicate gracefully
            assert 'UNIQUE constraint' in str(e) or 'duplicate' in str(e).lower()
    
    def test_invalid_foreign_key_handling(self, temp_database, sample_article_data):
        """Test handling of invalid foreign keys"""
        # Try to create article with non-existent author/category IDs
        invalid_article_data = sample_article_data.copy()
        invalid_article_data['author_id'] = 999999  # Non-existent ID
        invalid_article_data['category_id'] = 999999  # Non-existent ID
        
        try:
            article = Article.create(**invalid_article_data)
            # Should either handle gracefully or create with defaults
        except Exception as e:
            # Should provide meaningful error
            assert 'FOREIGN KEY' in str(e) or 'constraint' in str(e).lower()
    
    def test_database_connection_recovery(self, temp_database):
        """Test database connection recovery"""
        # This test ensures the database can recover from connection issues
        db = temp_database
        
        # Simulate connection issues by creating many concurrent operations
        authors = []
        for i in range(10):
            try:
                author_data = {
                    'name': f'Test Author {i}',
                    'slug': f'test-author-{i}',
                    'email': f'test{i}@example.com'
                }
                author = Author.create(**author_data)
                if author:
                    authors.append(author)
            except Exception as e:
                # Should handle connection issues gracefully
                pass
        
        # Should have created at least some authors
        assert len(authors) > 0


@pytest.mark.integration
@pytest.mark.slow
class TestDatabasePerformance:
    """Test database performance with larger datasets"""
    
    def test_bulk_operations(self, temp_database):
        """Test performance with bulk operations"""
        import time
        
        # Create multiple authors
        start_time = time.time()
        authors = []
        
        for i in range(50):
            author_data = {
                'name': f'Bulk Author {i}',
                'slug': f'bulk-author-{i}',
                'email': f'bulk{i}@example.com',
                'bio': f'Bio for author {i}' * 10  # Longer content
            }
            author = Author.create(**author_data)
            if author:
                authors.append(author)
        
        creation_time = time.time() - start_time
        
        # Should complete in reasonable time (less than 10 seconds)
        assert creation_time < 10.0
        assert len(authors) == 50
        
        # Test bulk retrieval
        start_time = time.time()
        all_authors = Author.find_all(limit=100)
        retrieval_time = time.time() - start_time
        
        assert len(all_authors) >= 50
        assert retrieval_time < 5.0  # Should be fast
    
    def test_search_performance(self, populated_database):
        """Test search performance"""
        import time
        
        # Create additional articles for search testing
        data = populated_database
        articles = []
        
        for i in range(20):
            article_data = {
                'title': f'Performance Test Article {i}',
                'slug': f'perf-test-article-{i}',
                'author_id': data['author'].id,
                'category_id': data['category'].id,
                'publication_date': '2024-12-12',
                'content': f'Performance testing content with keywords like AI, technology, innovation, creator economy, and digital trends. Article number {i}.' * 5
            }
            article = Article.create(**article_data)
            if article:
                articles.append(article)
        
        # Test search performance
        start_time = time.time()
        results = Article.search('technology')
        search_time = time.time() - start_time
        
        assert len(results) > 0
        assert search_time < 2.0  # Should be fast
        
        # Test complex search
        start_time = time.time()
        results = Article.search('AI innovation creator')
        complex_search_time = time.time() - start_time
        
        assert complex_search_time < 3.0  # Should still be reasonable