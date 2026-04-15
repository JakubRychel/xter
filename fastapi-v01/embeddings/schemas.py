from pydantic import BaseModel, Field
from typing import List, Tuple

class EmbedRequest(BaseModel):
    text: str

class EmbedResponse(BaseModel):
    embedding: List[float] = Field(..., min_items=512, max_items=512)

class GetNearestNeighborsRequest(BaseModel):
    query_vector: List[float] = Field(..., min_items=512, max_items=512)
    vectors: List[List[float]] = Field(..., min_items=1)
    k: int = 200
    d: int = 512

class FaissRawResponse(BaseModel):
    result: Tuple[
        List[List[float]],
        List[List[int]]
    ]