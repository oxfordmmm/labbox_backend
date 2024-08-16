import os

from dotenv import find_dotenv, load_dotenv

print("Script is being executed")


class Config:
    REQUIRED_KEYS = [
        "DATABASE_USER",
        "DATABASE_PASSWORD",
        "DATABASE_HOST",
        "DATABASE_PORT",
        "DATABASE_NAME",
        "AUTH0_DOMAIN",
        "AUTH0_API_AUDIENCE",
        "AUTH0_ALGORITHMS",
        "HOST",
        "PORT",
    ]

    def __init__(self):
        # Explicitly load the .env file
        load_dotenv(find_dotenv(), override=True, verbose=True)
        print(find_dotenv())

        self.DATABASE_USER = os.environ.get("DATABASE_USER", None)
        self.DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD", None)
        self.DATABASE_HOST = os.environ.get("DATABASE_HOST", None)
        self.DATABASE_PORT = os.environ.get("DATABASE_PORT", None)
        self.DATABASE_NAME = os.environ.get("DATABASE_NAME", None)
        self.AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", None)
        self.AUTH0_API_AUDIENCE = os.environ.get("AUTH0_API_AUDIENCE", None)
        self.AUTH0_ISSUER = os.environ.get("AUTH0_ISSUER", None)
        self.AUTH0_ALGORITHMS = [os.environ.get("AUTH0_ALGORITHMS", "RS256")]
        self.HOST = os.environ.get("HOST", "localhost:8000")
        self.PORT = os.environ.get("PORT", 8000)

        self.DATABASE_URL = (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )
        print(f"DATABASE_URL: {self.DATABASE_URL}")

    # @property
    # def DATABASE_URL(self):
    #     print("getting database url")
    #     return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"


config = Config()
