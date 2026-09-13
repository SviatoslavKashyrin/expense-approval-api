from fastapi import FastAPI
from app.api.endpoints import router as api_router, auth_router

app = FastAPI(title="Expense Approval API")

app.include_router(api_router)
app.include_router(auth_router)
@app.get("/")
def root():
    return {"message": "API is running"}