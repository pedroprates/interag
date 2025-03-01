from typing import Any
from langchain_openai import OpenAIEmbeddings
from consts.embeddings import Embeddings

__all__ = ["get_embedding"]

def get_embedding(type: str) -> Any:
    """
    Get a Embedding model based on type.

    Args:
        type (str): type of embedding model

    Returns:
        Any: Embeddings model object
    """
    match type:
        case "openai":
            return OpenAIEmbeddings(model=Embeddings.OPENAI_EMBEDDING_MODEL)
        case _:
            raise ValueError(f"Invalid embedding type {type}, currently valid embeddings: {', '.join(Embeddings.VALID_EMBEDDINGS)}")
