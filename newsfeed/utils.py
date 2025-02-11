from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from datetime import datetime
from .models import NewsSource, NewsArticle

def save_article(article_data):
    """
    Save a scraped article to the database.
    
    Args:
        article_data (dict): Dictionary containing article information
        Expected format:
        {
            'id': 'unique_id_string',
            'language': 'en',
            'title': 'Article Title',
            'source_name': 'Example News',
            'source_url': 'https://example.com',
            'href': 'https://example.com/article',
            'category': 'politics'
            'content': 'Article Content',
            'content_len': 1234,
            'sub_header': 'Article Subheader',
            'date': '2024-03-01T12:00:00Z'  # ISO format
        }
    """
    try:
        # Get or create the news source
        source, _ = NewsSource.objects.get_or_create(
            name=article_data['source_name'],
            defaults={'url': article_data['source_url']}
        )
        
        # Create or update the article
        article, created = NewsArticle.objects.update_or_create(
            id=article_data['id'],
            defaults={
                'language': article_data['language'],
                'title': article_data['title'],
                'source': source,
                'href': article_data['href'],
                'category': article_data['category'],
                'content': article_data['content'],
                'content_len': article_data['content_len'],
                'sub_header': article_data.get('sub_header'),  # Using get() as it might be None
                'date': article_data['date']
            }
        )

        updated = created == False
        
        return article, created, updated
    
    except Exception as e:
        print(f"Error saving article: {str(e)}")
        return None, False, False

def query_articles(
    source_name=None,
    language=None,
    category=None,
    start_date=None,
    end_date=None,
    keyword=None,
    min_length=None,
    limit=100
):
    """
    Query articles with various filters.
    
    Args:
        source_name (str): Filter by source name
        language (str): Filter by language code
        start_date (datetime): Filter articles published after this date
        end_date (datetime): Filter articles published before this date
        keyword (str): Search in title and content
        min_length (int): Minimum content length
        limit (int): Maximum number of articles to return
    """
    queryset = NewsArticle.objects.all()
    
    if source_name:
        queryset = queryset.filter(source__name=source_name)
    
    if language:
        queryset = queryset.filter(language=language)

    if category:
        queryset = queryset.filter(category=category)
    
    if start_date:
        queryset = queryset.filter(date__gte=start_date)
    
    if end_date:
        queryset = queryset.filter(date__lte=end_date)
    
    if keyword:
        queryset = queryset.filter(
            models.Q(title__icontains=keyword) |
            models.Q(content__icontains=keyword)
        )
    
    if min_length:
        queryset = queryset.filter(content_len__gte=min_length)
    
    return list(queryset.order_by('-date')[:limit])