from typing import Literal
from langchain_chroma import Chroma
from embeddings import get_embedding


class VectorStore:
    def __init__(
        self, collection_name: str = "interag", embedding: Literal["openai"] = "openai"
    ):
        embedding_model = get_embedding(embedding)
        self.collection_name = collection_name

        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=embedding_model,
            persist_directory="./interag_db"
        )



