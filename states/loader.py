from typing_extensions import TypedDict


class LoaderState(TypedDict):
    document: str
    metadata: dict

    reviewed_document: str
