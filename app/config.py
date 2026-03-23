from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY:str
    DATABASE_URL:str
    ALGORITHM:str="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int=30
    S3_PROVIDER:str = "minio" #aws|minio|localstack
    S3_ENDPOINT_URL: str | None = None
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET_NAME: str
    S3_REGION:str = "us-east-1"
    REDIS_URL:str

    class Config():
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()