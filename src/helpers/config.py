from pydantic_settings import BaseSettings , SettingsConfigDict

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str

    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE : int

    MONGODB_URL : str
    MONGODB_DATABASE : str

    GENERATION_BACKEND : str
    EMBEDDING_BACKEND : str

    OPENAI_API_KEY : str = None
    OPENAI_URL : str = None
    COHERE_API_KEY : str = None

    GENERATION_MODEL_ID : str = None
    EMBEDDING_MODEL_ID : str = None
    EMBEDDING_MODEL_SIZE : str = None

    INPUT_DEFAULT_MAX_CHARACHTERS : int = None
    GENERATION_DEFAULT_MAX_TOKENS : int = None
    GENERATION_DEFAULT_TEMPERATURE : float = None

    class Config(SettingsConfigDict):
        env_file = ".env"

def get_settings():
    return Settings()