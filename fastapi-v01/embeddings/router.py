from fastapi import APIRouter
from embeddings.services.faiss_service import get_nearest_neighbors
from embeddings.services.sentence_transformer_service import embed
from embeddings.schemas import EmbedRequest, EmbedResponse, GetNearestNeighborsRequest, FaissRawResponse

router = APIRouter(tags=['embeddings'])

@router.post('/embed', response_model=EmbedResponse)
def embed_endpoint(payload: EmbedRequest):
    embedding = embed(payload.text)

    return {'embedding': embedding}

@router.post('/get-nearest-neighbors', response_model=FaissRawResponse)
def get_nearest_neighbors_endpoint(payload: GetNearestNeighborsRequest):
    result = get_nearest_neighbors(
        payload.query_vector,
        payload.vectors,
        payload.k,
        payload.d
    )

    return {'result': result}