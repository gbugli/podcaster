from django.db import models
from django.utils import timezone

class NewsSource(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    
    def __str__(self):
        return self.name

class NewsArticle(models.Model):
    # Using the provided ID from JSON instead of auto-increment
    id = models.CharField(max_length=100, primary_key=True)
    language = models.CharField(max_length=10)
    title = models.CharField(max_length=500)
    source = models.ForeignKey(NewsSource, on_delete=models.CASCADE)
    href = models.URLField()
    category = models.CharField(max_length=500)
    content = models.TextField()
    content_len = models.IntegerField()
    sub_header = models.TextField(null=True, blank=True)
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['language']),
            models.Index(fields=['source']),
        ]