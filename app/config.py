from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY:str
    DATABASE_URL:str
    ALGORITHM:str="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int=30

    class Config():
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()