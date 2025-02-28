import logging
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig, BrowserConfig, CacheMode
from crawler.queue import URLQueue

logger = logging.getLogger(__name__)

class Crawler:
    """ Crawler class responsible to crawl the URL and all the internal links referenced on it """
    def __init__(self, url: str, media: bool = False, verbose: bool = True):
        self._url = url
        self._media = media
        self.verbose = verbose

        self.browser_config = BrowserConfig(verbose=self.verbose)
        self.crawler_config = CrawlerRunConfig(
            word_count_threshold=10,
            exclude_external_links=True,
            remove_overlay_elements=True,
            process_iframes=True,
            excluded_tags=["form"],
            cache_mode=CacheMode.ENABLED,
        )
        self.queue = URLQueue()
        self.queue.add(url)

    async def crawl(self):
        
        # TODO: Docstring
        # TODO: Logging with verbose
        # TODO: Implement media
        # TODO: Implement saving heap

        while not self.queue.empty():
            url_to_fetch = self.queue.pop()

            if self.verbose:
                logging.info(f"Fetching {url_to_fetch}, {len(self.queue)} links left.")

            async with AsyncWebCrawler(browser_config=self.browser_config) as crawler:
                result = await crawler.arun(
                    url=url_to_fetch,
                    config=self.crawler_config
                )

                if not result.success:
                    raise RuntimeError("Something bad happened.")

