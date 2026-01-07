import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer('distiluse-base-multilingual-cased-v2')

def embed(text):
    return embedding_model.encode(text)

def get_nearest_neighbors(query_vector, vectors, k=200, d=512):
    query_vector = np.asarray([query_vector], dtype='float32')
    vectors = np.asarray(vectors, dtype='float32')

    index = faiss.IndexFlatIP(d)
    faiss.normalize_L2(query_vector)
    faiss.normalize_L2(vectors)

    index.add(vectors)

    result = index.search(query_vector, k=k)

    return result # (D, I) D - odległość, I - indeks
