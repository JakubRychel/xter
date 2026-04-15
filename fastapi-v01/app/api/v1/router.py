from fastapi import APIRouter
from app.api.v1.routes import embeddings, genai, recommendations

router = APIRouter(prefix='/v1')

router.include_router(embeddings.router)
router.include_router(genai.router)
router.include_router(recommendations.router)