from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    chunk_words: int = 300
    chunk_overlap: int = 50
