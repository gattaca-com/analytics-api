from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_host: str
    db_port: int = 5432
    db_name: str = "ethereum"
    db_user: str
    db_password: str

    db_pool_min: int = 2
    db_pool_max: int = 10

    max_limit: int = 1000
    default_limit: int = 100
    max_range_seconds: int = 21600
    # relay.bid_submission is a very large hypertable — cap ranges tighter
    bid_submission_max_range_seconds: int = 3600
    statement_timeout_seconds: int = 15

    # Per-client-IP rate limits (requests/minute). 0 disables.
    rate_limit_per_minute: int = 120
    rate_limit_heavy_per_minute: int = 20


settings = Settings()
