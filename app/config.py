import os
from dataclasses import dataclass


@dataclass
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    db_url: str = os.getenv("DATABASE_URL", "sqlite:///./smartcore.db")
    api_host: str = os.getenv("FASTAPI_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("FASTAPI_PORT", "8000"))
    streamlit_host: str = os.getenv("STREAMLIT_HOST", "0.0.0.0")
    streamlit_port: int = int(os.getenv("STREAMLIT_PORT", "8501"))
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")


settings = Settings()
