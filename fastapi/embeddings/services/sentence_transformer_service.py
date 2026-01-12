from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer('distiluse-base-multilingual-cased-v2')

def embed(text):
    return embedding_model.encode(text)