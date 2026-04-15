from fastapi import FastAPI
from app.api.v1.router import router

app = FastAPI(title='Xter FastAPI Service')

app.include_router(router)