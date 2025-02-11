import os
import sys
import django
from podcaster.config import config

# Add project root to Python path
project_root = config.get('projectRoot')
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils.timezone import make_naive
from newsfeed.utils import query_articles
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import date, datetime


INTERESTS = config.get('interests')

def find_similar_with_embeddings(articles_text, interests=None, similarity_threshold=0.6):
    # Load model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Get embeddings
    embeddings = model.encode(articles_text)
    interests_embedding = model.encode(interests)
    
    # Calculate similarity
    similarity_matrix = cosine_similarity(embeddings)

    if interests:
        interests_similarity_matrix = cosine_similarity(embeddings, interests_embedding)
        scores = np.max(interests_similarity_matrix, axis=1)
    else:
        scores = np.ones(len(articles_text))
    
    unique_indices = []
    duplicate_indices = set()
    
    for i in range(len(articles_text)):
        if i not in duplicate_indices:
            unique_indices.append(i)
            # Find similar articles
            for j in range(i + 1, len(articles_text)):
                if similarity_matrix[i][j] > similarity_threshold:
                    duplicate_indices.add(j)

    return unique_indices, scores

def compute_scores(all_articles, title_scores, summary_scores):
    today = date.today()
    lens = np.array([article.content_len for article in all_articles])
    normal_lens = (lens - np.min(lens)) / (np.max(lens) - np.min(lens))
    recency = 1 / np.array([(datetime(today.year, today.month, today.day) - make_naive(article.date)).days + 1 for article in all_articles])

    total_scores = 0.6*(0.7*title_scores + 0.3*summary_scores) + 0.2*(normal_lens) + 0.2*(recency)
    return total_scores

def compare_multilingual_embeddings(category, start_date=None, end_date=None, score_threshold=0.3, min_lenght=None):

    all_articles = query_articles(category=category, start_date=start_date, end_date=end_date, min_length=min_lenght)
    all_titles = [a.title for a in all_articles]
    all_summaries = [a.sub_header for a in all_articles]

    unique_titles_ids, title_scores = find_similar_with_embeddings(all_titles, INTERESTS, 0.675)
    unique_summaries_ids, summary_scores = find_similar_with_embeddings(all_summaries, INTERESTS, 0.85)

    total_scores = compute_scores(all_articles, title_scores, summary_scores)

    unique_indices = set(unique_titles_ids).intersection(set(unique_summaries_ids))
    interesting_indices = np.where(total_scores > score_threshold)[0]

    indices = unique_indices.intersection(set(interesting_indices))
    pairs = [(idx, total_scores[idx]) for idx in indices]
    sorted_pairs = sorted(pairs, key=lambda x: x[1], reverse=True)
    sorted_indices = [pair[0] for pair in sorted_pairs]

    selected_articles = [all_articles[i] for i in sorted_indices]

    return selected_articles