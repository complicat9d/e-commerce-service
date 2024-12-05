import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_HOST: str = "db"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    DATABASE_DB: str = "postgres"

    TOKEN: str
    BOT_NAME: str
    BOT_PAYMENT_PROVIDER_TOKEN: str

    EXCEL_FILE_PATH: str = os.path.join(os.getcwd(), "data/orders.xlsx")

    CHANNEL_SUBSCRIPTION_LINK: str = "https://t.me/dlgmdlgkdlgkdgl"
    CHANNEL_SUBSCRIPTION_CHECK: str = "https://t.me/dlgmdlgkdlgkdgl"
    GROUP_SUBSCRIPTION_LINK: str = "https://t.me/dkgkldkgldgkdg"
    GROUP_SUBSCRIPTION_CHECK: str = "-1002494342292"  # chat_id: 2494342292

    SECRET_KEY: str

    DEBUG_ENGINE: bool = False


settings = Settings()
