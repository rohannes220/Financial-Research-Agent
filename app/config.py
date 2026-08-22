from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/financial_agent"
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4.1-mini"
    openai_embed_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    sec_user_agent: str = "FinancialResearchAgent contact@example.com"
    top_k: int = 6
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()
