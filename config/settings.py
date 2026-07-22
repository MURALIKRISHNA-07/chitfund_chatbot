import os
from pathlib import Path
from dotenv import dotenv_values

BASE_DIR = Path(__file__).resolve().parent.parent

# Optionally load .env (does not modify os.environ)
env_file = BASE_DIR / ".env"
env_config = dotenv_values(env_file) if env_file.exists() else {}


def get_env(key, default=""):
    """
    Priority:
    1. OS environment variable
    2. .env file (if present)
    3. Default value
    """
    
    return os.getenv(key) or env_config.get(key) or default


# =========================
# Gemini
# =========================

GEMINI_API_KEY = get_env("GEMINI_API_KEY")

GEMINI_EMBEDDING_MODEL = get_env(
    "GEMINI_EMBEDDING_MODEL",
    "gemini-embedding-001",
)

GEMINI_CHAT_MODEL = get_env(
    "GEMINI_CHAT_MODEL",
    "gemini-2.0-flash",
)


# =========================
# Qdrant
# =========================

QDRANT_HOST = get_env(
    "QDRANT_HOST",
    "localhost",
)

QDRANT_PORT = int(
    get_env(
        "QDRANT_PORT",
        "6333",
    )
)

QDRANT_URL = get_env("QDRANT_URL")

QDRANT_API_KEY = get_env("QDRANT_API_KEY")

QDRANT_COLLECTION = get_env(
    "QDRANT_COLLECTION",
    "chitfund_knowledge",
)


# =========================
# MongoDB
# =========================

MONGODB_URI = get_env(
    "MONGODB_URI",
    "mongodb://localhost:27017",
)

MONGODB_DB = get_env(
    "MONGODB_DB",
    "chitfund_chat",
)


# =========================
# Other
# =========================

SCHEMES_API_URL = get_env("SCHEMES_API_URL")

FOREMAN_COMMISSION_RATE = float(
    get_env(
        "FOREMAN_COMMISSION_RATE",
        "1.5",
    )
)




SCHEMES_JSON_PATH = BASE_DIR / "schemes.json"
PDF_PATH = BASE_DIR / "documents" / "chitfunds.pdf"


# Debug
print(f".env found: {env_file.exists()}")
print("Gemini key loaded:", bool(GEMINI_API_KEY))
print("Gemini model:", GEMINI_CHAT_MODEL)