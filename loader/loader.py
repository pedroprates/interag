import os
import json
import logging
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from langchain_openai import ChatOpenAI
from playwright.async_api import Response
from utils.queue import UniqueQueue
from states.loader import LoaderState, GarbageCollectorStructure, RewriterStructure
from loader.vector_store import VectorStore
from prompts.loader import GARBAGE_COLLECTOR_PROMPT, REWRITER_PROMPT

logger = logging.getLogger(__name__)

# TODO: Send async calls for graph
# TODO: Limit the number of asyncs calls for graph?
# TODO: Build graph best way possible, what defines a node?

class DocumentLoader:
    def __init__(self, base_path: str = "data"):
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

        metadata_file = os.path.join(self._base_path, "metadata.json")

        with open(metadata_file, "r") as file:
            metadata = json.load(file)

        for m in metadata:
            queue.add(m)

        return queue


    def manager_node(self, state: LoaderState):
        """
        """
        send_statement = []
        for _ in range(len(self.all_documents)):
            if not self.all_documents.empty():
                document = self.all_documents.pop()

                if not isinstance(document, dict):
                    raise ValueError(f"Document expected type dict, got {type(document)} instead")

                _metadata = {key: value for key, value in document.items() if key in ["url", "title", "description"]}
                with open(document["path"], "r") as file:
                    doc = file.read()

                send_statement.append(Send("garbage_collector", {"document": doc, "metadata": _metadata}))

        return send_statement

    def garbage_collector(self, state: LoaderState) -> dict:
        """
        """
        model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        prompt = GARBAGE_COLLECTOR_PROMPT.format(CONTENT=state["document"])

        response = model.with_structured_output(GarbageCollectorStructure).invoke(prompt)

        if not isinstance(response, GarbageCollectorStructure):
            raise ValueError(f"Response was expecting GarbageCollectorStructure, got {type(response)} instead")

        return {"document": response.clean_document}

    def rewrite_document(self, state: LoaderState):
        """
        """
        model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        metadata = state.get("metadata")

        if not metadata:
            raise ValueError("Metadata not found")

        prompt = REWRITER_PROMPT.format(
            TITLE=metadata.get("title", ""),
            DESCRIPTION=metadata.get("description", ""),
            CONTENT=state["document"]
        )

        response = model.with_structured_output(RewriterStructure).invoke(prompt)

        if not isinstance(response, RewriterStructure):
            raise ValueError(f"Response was expecting RewriterStructure, got {type(response)} instead")

        return {"reviewed_document": response.rewritten_document}

    def stores_document(self, state: LoaderState):
        pass

    def _graph(self):
        """
        """
        graph = StateGraph(LoaderState)

        # graph.add_node("manager_node", self.manager_node)
        graph.add_node("garbage_collector", self.garbage_collector)
        graph.add_node("rewrite_document", self.rewrite_document)
        # graph.add_node("stores_document", self.stores_document)

        graph.add_conditional_edges(START, self.manager_node)
        graph.add_edge("garbage_collector", "rewrite_document")
        graph.add_edge("rewrite_document", END)

        model = graph.compile()

        return model

