import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for SqlAgent"""

    # MySQL Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'test')

    # LLM Provider Configuration
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'ollama')  # "ollama" or "gemini"

    # Ollama Configuration
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')

    # Gemini Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')

    # ChromaDB Configuration
    CHROMA_PERSIST_DIR = os.getenv('CHROMA_PERSIST_DIR', './chroma_data')
    SCHEMA_CACHE_ENABLED = os.getenv('SCHEMA_CACHE_ENABLED', 'true').lower() == 'true'
    SCHEMA_AUTO_TRAIN = os.getenv('SCHEMA_AUTO_TRAIN', 'true').lower() == 'true'

    @classmethod
    def get_mysql_connection_string(cls):
        """Generate MySQL connection string"""
        return f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        required = ['DB_USER', 'DB_NAME']
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        return True
