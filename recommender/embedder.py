# recommender/embedder.py

import numpy as np
from sentence_transformers import SentenceTransformer

# Load the model once
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_job_embeddings(skills_list):
    """
    Generate and save embeddings for a list of job skills.
    """
    embeddings = model.encode(skills_list, show_progress_bar=True)
    np.save("data/job_embeddings.npy", embeddings)
    print(f"Embeddings for {len(skills_list)} jobs saved to data/job_embeddings.npy")


def generate_embedding(text):
    """
    Generate an embedding for a single user input string.
    """
    return model.encode([text])[0]
