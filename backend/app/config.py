from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://portal:portal@db:5432/portal"
    admin_user_ids: str = "1"

    @property
    def admin_ids(self) -> set[int]:
        return {int(x.strip()) for x in self.admin_user_ids.split(",") if x.strip()}


settings = Settings()
