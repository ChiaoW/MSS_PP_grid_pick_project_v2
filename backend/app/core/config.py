import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./grid_allocator_dev.db")
    API_BASE_URL = os.getenv("API_BASE_URL", "").rstrip('/')
    API_USERNAME = os.getenv("API_USERNAME", "")
    API_PASSWORD = os.getenv("API_PASSWORD", "")
    CLIENT_IP = os.getenv("CLIENT_IP", "")

settings = Settings()