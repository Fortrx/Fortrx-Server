from pathlib import Path
from urllib.parse import urlparse

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    SECRET_KEY: str
    DATABASE_URL: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SQL_ECHO: bool = False
    PUBLIC_BASE_URL: str = "http://localhost:8000"
    ALLOWED_HOSTS: str = ""
    DEPLOY_ENV: str = "local"
    S3_PROVIDER: str = "minio"  # aws|minio|localstack
    S3_ENDPOINT_URL: str | None = None
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET_NAME: str
    S3_REGION: str = "us-east-1"
    REDIS_URL: str
    RATE_LIMIT_STORAGE: str = "memory://"
    MAX_SEALED_BLOB_BYTES: int = 262144
    MAX_MESSAGE_TTL_SECONDS: int = 604800

    @field_validator(
        "SECRET_KEY",
        "DATABASE_URL",
        "S3_ACCESS_KEY",
        "S3_SECRET_KEY",
        "S3_BUCKET_NAME",
        "REDIS_URL",
        "RATE_LIMIT_STORAGE",
    )
    @classmethod
    def _require_non_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Environment value must not be blank.")
        return value

    @field_validator("SECRET_KEY")
    @classmethod
    def _validate_secret_key(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long.")
        return value

    @field_validator("PUBLIC_BASE_URL")
    @classmethod
    def _normalize_public_base_url(cls, value: str) -> str:
        value = value.strip()
        return value.rstrip("/")

    @staticmethod
    def _normalize_host_entry(value: str) -> str | None:
        value = value.strip().rstrip("/")
        if not value:
            return None

        if "://" not in value:
            parsed = urlparse(f"//{value}")
        else:
            parsed = urlparse(value)

        host = parsed.hostname
        if host:
            return host

        raw_host = parsed.path.split("/", 1)[0].strip()
        if not raw_host:
            return None
        if raw_host.startswith("*."):
            return raw_host
        return raw_host.split(":", 1)[0]

    @property
    def trusted_hosts(self) -> list[str]:
        hosts = ["localhost", "127.0.0.1", "testserver"]
        public_host = self._normalize_host_entry(self.PUBLIC_BASE_URL)
        if public_host:
            hosts.append(public_host)
        if self.ALLOWED_HOSTS:
            hosts.extend(
                normalized_host
                for host in self.ALLOWED_HOSTS.split(",")
                if (normalized_host := self._normalize_host_entry(host))
            )
        return list(dict.fromkeys(hosts))


settings = Settings()
