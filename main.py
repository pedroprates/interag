import logging
import asyncio
from crawler import Crawler
from loader.loader import DocumentLoader

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# TODO: FastAPI for CLI?
# TODO: Create a Vector DB locally?
# TODO: Free embedding?
# Chroma: https://docs.trychroma.com/docs/overview/getting-started
# LangChain + Chroma: https://python.langchain.com/docs/integrations/vectorstores/chroma/


if __name__ == "__main__":

    # URL = "https://workable.readme.io/reference/generate-an-access-token"
    # crawler = Crawler(url=URL, media=True, verbose=True, fit_markdown=False)
    # asyncio.run(crawler.crawl())
    
    load = DocumentLoader()

    load._graph()

