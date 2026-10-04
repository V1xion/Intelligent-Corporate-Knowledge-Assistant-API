from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_provider: str = "openai"

    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6-luna"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 700
    chunk_overlap: int = 100
    top_k: int = 4
    similarity_threshold: float = 0.35
    collection_name: str = "corporate_knowledge"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
