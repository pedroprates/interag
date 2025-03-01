from uuid import uuid4
from typing import Literal
from langchain_chroma import Chroma
from langchain_core.documents import Document
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

    def add_document(self, content: str, metadata: dict) -> str:
        """
        Add a single document and its metadata on VectorStore, with its metadata

        Args:
            content (str): content of the document
            doc_metadata (dict): metadata of the document

        Returns:
            str: id of the document
        """
        id = uuid4()
        doc = Document(
            page_content=content,
            metadata=metadata,
            id=id
        )

        self.vector_store.add_documents(documents=[doc], ids=[id])

        return str(id)


    def add_documents(self, documents: list[dict]) -> list[dict]:
        """
        Adds documents in batches on VectorStore, the documents must be in a dictionary (list of dictionaries for a batch).

        Each document should follow the same structure, containing the content and metadata:

        ```python
        doc = {
            "page_content": "content of the document, string",
            "metadata": "metadata for the document, dictionary"
        }
        ```

        Args:
            documents (list[dict] | dict): a list of documents with a controlled structure

        Returns:
            list[dict]: same list of documents, now with the following IDs from the VectorStore
        """
        documents = documents if isinstance(documents, list) else [documents]

        docs = [{
            **doc,
            "id": uuid4()
        } for doc in documents]

        document_list = [Document(**doc) for doc in docs]

        self.vector_store.add_documents(documents=document_list, ids=[doc["id"] for doc in docs])

        return docs

    def query(self, query: str, k: int = 2, filter: dict = {}) -> list[dict]:
        """
        Perform a similarity search on the VectorStore, returning the top k results

        Args:
            query (str): string to search for
            k (int): number of closest documents on the similarity search, defaults to 2.
            filter (dict): how to filter the available data, defaults to no-filter.
            
        Returns:
            list[dict]: list of results, with `content` and `metadata` keys.
        """
        results = self.vector_store.similarity_search(query, k=k, filter=filter)

        result = [{
            "content": res.page_content,
            "metadata": res.metadata
        } for res in results]

        return result
