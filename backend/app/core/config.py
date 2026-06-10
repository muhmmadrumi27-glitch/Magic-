from pydantic import BaseSettings, Field, AnyUrl

class Settings(BaseSettings):
    app_name: str = "KeyaZ Agent"
    api_v1_str: str = "/api/v1"
    backend_cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    postgres_user: str = Field(..., env="POSTGRES_USER")
    postgres_password: str = Field(..., env="POSTGRES_PASSWORD")
    postgres_db: str = Field(..., env="POSTGRES_DB")
    postgres_server: str = Field("postgres", env="POSTGRES_SERVER")
    database_url: AnyUrl | None = None

    redis_url: str = Field("redis://redis:6379/0", env="REDIS_URL")
    chroma_url: str = Field("http://chromadb:8000", env="CHROMA_URL")
    browserless_ws: str = Field("ws://browserless:3000?--timeout=60000", env="BROWSERLESS_WS")
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    fernet_key: bytes = Field(..., env="FERNET_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.database_url:
            return str(self.database_url)
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_server}/{self.postgres_db}"

settings = Settings()