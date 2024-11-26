
import time
import random
import math
import statistics

def add_random_delay(min_seconds=5, max_seconds=15):
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)

def calculate_weighted_score(book, avg_rating, M=50, alpha=1.3):
    R = book['rating']
    v = book['reviews_count']
    if v == 0:
        return 0
    weighted_score = ((R ** alpha * v) + (M * avg_rating)) / (v + M) * math.log(v + 1)
    return weighted_score

def calculate_weighted_scores_for_books(books, M=50, alpha=1.3):
    avg_rating = statistics.mean(book['rating'] for book in books if book['reviews_count'] >= M)

    for book in books:
        book['weighted_score'] = calculate_weighted_score(book, avg_rating, M, alpha)
    
    books.sort(key=lambda x: (-x['weighted_score'], -x['reviews_count']))
    return books
