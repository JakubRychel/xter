from fastembed import FastEmbed

class FastEmbedService:
    def __init__(self):
        self.model_name = 'all-MiniLM-L6-v2' # 384-wymiarowy
        self.embedder = FastEmbed(model_name=self.model_name)

    def embed(self, text: str) -> list[float]:
        return self.embedder.embed(text)
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return self.embedder.embed_batch(texts)