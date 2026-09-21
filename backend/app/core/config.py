import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Senac TechLab - Gestão de Ativos de TI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # SQLite assíncrono por padrão, ou PostgreSQL via DATABASE_URL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite+aiosqlite:///./senac_assets.db"
    )

    class Config:
        case_sensitive = True

settings = Settings()
