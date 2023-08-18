# app/core/config.py

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_title: str = 'Кошачий благотворительный фонд (0.1.0)'
    app_description: str = ('Сервис для поддержки котиков!')
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'secret'

    class Config:
        env_file = '.env'


settings = Settings()
