from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Code Review + Secret Leakage Detection Platform"
    db_url: str = "sqlite:///./app.db"
    llm_provider: str = "mock"
    openai_base_url: str = "https://api.openai.com/v1"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    demo_repo_path: str = "../demo/vulnerable_repo"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")


settings = Settings()
