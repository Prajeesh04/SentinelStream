from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REDIS_URL: str = 'redis://localhost:6379/0'
    CELERY_BROKER_URL: str = 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND: str = 'redis://localhost:6379/2'
    DEBUG: bool = False
    ML_MODEL_PATH: str = 'ml/fraud_model.joblib'
    ML_RISK_THRESHOLD: float = 0.7
    RATE_LIMIT_PER_MINUTE: int = 1000
    ALLOWED_ORIGINS: str = 'http://localhost:3000'

    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def _parse_origins(cls, v):
        if isinstance(v, list):
            return ','.join(v)
        return v

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(',') if o.strip()]

    class Config:
        env_file = '.env'


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
