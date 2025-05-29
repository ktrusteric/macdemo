from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # 项目信息
    PROJECT_NAME: str = "Energy Info System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "energy_info"
    
    # AI集成配置
    AI_BACKEND_URL: str = "https://ai.wiseocean.cn"
    AI_API_TIMEOUT: int = 30
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置 - 同时支持localhost和公网IP
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://14.103.245.50:5173",
        "http://14.103.245.50:3000",
        "http://14.103.245.50:8080"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()