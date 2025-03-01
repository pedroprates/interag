import os
from consts.variables import Credentials

__all__ = ["check_credentials"]


def check_credentials(product: str):
    """
    Checks for credentials for a given product
    """

    match product:
        case "openai":
            cred = os.getenv(Credentials.OPENAI)

            if not cred:
                raise ValueError(f"Missing OpenAI key, should be at {Credentials.OPENAI}")

        case _:
            return
