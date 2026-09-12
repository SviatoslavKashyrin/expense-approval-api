from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/expense_db"
    OPENAI_API_KEY: str = "your-openai-api-key"

    class Config:
        env_file = ".env"


settings = Settings()