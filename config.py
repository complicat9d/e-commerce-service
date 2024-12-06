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
    BOT_PAYMENT_PROVIDER_TOKEN: str

    EXCEL_FILE_PATH: str = os.path.join(os.getcwd(), "data/orders.xlsx")

    CHANNEL_SUBSCRIPTION_LINK: str
    CHANNEL_SUBSCRIPTION_CHECK: str
    GROUP_SUBSCRIPTION_LINK: str
    GROUP_SUBSCRIPTION_CHECK: str

    SECRET_KEY: str = "django-insecure-%)78vsoln&u5-#5sj8=8c%-dpo)yco-!g=bxm5j(_08afhf#m1"
    DJANGO_SUPERUSER_PASSWORD: str
    DJANGO_SUPERUSER_EMAIL: str

    DEBUG_ENGINE: bool = False


settings = Settings()
