from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.db_url import get_database_url, normalize_database_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://portal:portal@db:5432/portal"
    admin_user_ids: str = "1"

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_db_url(cls, value):
        if not value:
            return get_database_url()
        return normalize_database_url(str(value))

    @property
    def admin_ids(self) -> set[int]:
        return {int(x.strip()) for x in self.admin_user_ids.split(",") if x.strip()}


settings = Settings()
