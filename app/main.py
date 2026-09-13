from fastapi import FastAPI
from app.api.endpoints import router as api_router

app = FastAPI(title="Expense Approval API")

app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "API is running"}