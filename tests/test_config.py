# py path for /src added in .toml file. only then was src/finrag/config accessible from this file.
from finrag.config import Settings


def test_settings():
    settings = Settings()
    assert settings.chunk_words == 300
    assert settings.chunk_overlap == 50


# def test_chunk_words_len(chunk_words: int):
#     assert chunk_words == 300


# def test_chunk_overlap_len(chunk_overlap: int):
#     assert chunk_overlap == 50
