from typing_extensions import TypedDict
from pydantic import BaseModel, Field


class LoaderState(TypedDict):
    document: str | None
    metadata: dict | None

    reviewed_document: str | None

class GarbageCollectorStructure(BaseModel):
    clean_document: str = Field(description="Clean document, without any garbage.")

class RewriterStructure(BaseModel):
    rewritten_document: str = Field(description="Rewritten document from API documentation")
