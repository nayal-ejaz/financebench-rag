from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    chunk_words: int = 300
    # chunk_overlap: int = 50
    chunk_overlap: int = Field(default=50, ge=0)    # Field(...) attaches extra rules to a field.



