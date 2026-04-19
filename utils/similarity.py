from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def detect_duplicates(reviews):
    """
    Given a list of review dictionaries, detects duplicate or highly similar reviews.
    Adds a 'repeated_pattern' flag to the review dict if it's too similar to another.
    """
    if len(reviews) < 2:
        for r in reviews:
            r['is_duplicate'] = False
        return reviews
        
    texts = [r['text'] for r in reviews]
    vectorizer = TfidfVectorizer()
    
    try:
        tfidf_matrix = vectorizer.fit_transform(texts)
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Identify rows where similarity with any preceding row is > 0.85
        for i in range(len(texts)):
            is_dup = False
            for j in range(i):
                if similarity_matrix[i][j] > 0.85:
                    is_dup = True
                    break
            reviews[i]['is_duplicate'] = is_dup
    except Exception as e:
        # If vectorization fails (e.g. all empty strings), just mark as false
        for r in reviews:
            r['is_duplicate'] = False
            
    return reviews
