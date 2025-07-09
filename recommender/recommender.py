# recommender/recommender.py

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def recommend_jobs(user_embedding, df, top_n=5, threshold=0.4):
    try:
        job_embeddings = np.load("data/job_embeddings.npy")
    except FileNotFoundError:
        print("❌ Job embeddings not found. Please generate them first.")
        return []

    similarities = cosine_similarity([user_embedding], job_embeddings)[0]
    top_indices = similarities.argsort()[::-1]
    
    results = []
    for idx in top_indices:
        if similarities[idx] >= threshold:
            results.append((idx, similarities[idx]))
            if len(results) >= top_n:
                break
    return results
