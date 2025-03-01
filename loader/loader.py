import os
import logging
from langgraph.graph import StateGraph
from utils.queue import UniqueQueue
from states.loader import LoaderState
from loader.vector_store import VectorStore

logger = logging.getLogger(__name__)


class DocumentLoader:
    def __init__(self, base_path: str = "data/pages"):
        self._base_path = base_path

        self.all_documents: UniqueQueue = self.get_all_documents()
        self.store = VectorStore()


    def get_all_documents(self) -> UniqueQueue:
        """
        Get all documents path and returns.

        Returns:
            UniqueQueue: list of all documents paths
        """
        queue = UniqueQueue()

        for root, _, files in os.walk(self._base_path):
            for file in files:
                if file.endswith(".md"):
                    queue.add(os.path.join(self._base_path, root, file))

        logging.info(f"Found {len(queue)} documents")

        return queue


    def garbage_collector(self, state: LoaderState):
        pass

    def rewrite_document(self, state: LoaderState):
        pass

    def stores_document(self, state: LoaderState):
        pass

    def _graph(self):
        """
        """
        graph = StateGraph(LoaderState)

        graph.add_node("garbage_collector", self.garbage_collector)
        graph.add_node("rewrite_document", self.rewrite_document)
        graph.add_node("stores_document", self.stores_document)
