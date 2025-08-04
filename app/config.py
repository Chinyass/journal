from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):

    # RabbitMQ параметры
    RABBITMQ_HOST: str = Field("localhost", env="RABBITMQ_HOST")
    RABBITMQ_PORT: int = Field(5672, env="RABBITMQ_PORT")
    RABBITMQ_USER: str = Field("guest", env="RABBITMQ_USER")
    RABBITMQ_PASSWORD: str = Field("guest", env="RABBITMQ_PASSWORD")
    
    # MongoDB параметры
    MONGODB_URL: str = Field("mongodb://localhost:27017", env="MONGODB_URL")
    MONGODB_DB: str = Field("dbname", env="MONGODB_DB")
    MONGODB_USER: str = Field("admin", env="MONGODB_USER")
    MONGODB_PASSWORD: str = Field("password", env="MONGODB_PASSWORD")
    MONGODB_AUTH_SOURCE: str = "admin"

    # Netbox параметры
    NETBOX_URL: str = Field("http://localhost:8000", env="NETBOX_URL")
    NETBOX_TOKEN: str = Field("token", env="NETBOX_TOKEN")

    
    class Config:
        env_file = ".env"

settings = Settings()