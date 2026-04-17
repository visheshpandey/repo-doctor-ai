from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    openai_api_key: str = ""
    temp_repos_dir: str = os.path.join(os.path.dirname(__file__), "temp_repos")
    reports_dir: str = os.path.join(os.path.dirname(__file__), "reports")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
