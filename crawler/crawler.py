import os
import random
import logging
from crawl4ai import AsyncWebCrawler
from crawl4ai.models import CrawlResult, MarkdownGenerationResult
from crawl4ai.async_configs import CrawlerRunConfig, BrowserConfig, CacheMode
from crawler.queue import URLQueue

logger = logging.getLogger(__name__)

class Crawler:
    """ Crawler class responsible to crawl the URL and all the internal links referenced on it """
    def __init__(self, url: str, media: bool = False, verbose: bool = True, fit_markdown: bool = False):
        self._url = url
        self._media = media
        self.verbose = verbose
        self._fit_markdown = fit_markdown
        self._base_data_path = "data"

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

    @staticmethod
    def __parse_markdown(
        result: CrawlResult, fit: bool = False
    ) -> str:
        """
        Parses markdown result from Crawler, it could be a fit version (it could be from markdown or markdown_v2),
        understands the possible file formats and returns it as a string.

        Args:
            result (CrawlResult): result from the crawler
            fit (bool): if fit is enabled, defaults to False

        Returns:
            str: markdown file as string
        """
        _result = result.markdown_v2 if fit else result.markdown

        if isinstance(_result, MarkdownGenerationResult):
            mkdwn = _result.fit_markdown if fit else _result.raw_markdown
        elif isinstance(_result, str):
            mkdwn = _result
        else:
            raise ValueError(f"Could not parse Markdown result: {_result}")

        if not mkdwn:
            raise ValueError(f"Could not parse Markdown result: {_result}")

        return mkdwn


    def _save_file(self, response: CrawlResult) -> dict:
        """
        Saves the result file from the crawl on a markdown file inside data folder.

        Args:
            response (CrawlResult): The result of the crawl

        Returns:
            dict: metadata with information of the saved file
        """
        metadata: dict = response.metadata if response.metadata else {}

        _title = metadata.get("title")
        _description = metadata.get("description")

        title = f"unnamed_file_{random.randint(0, 1000)}" if not _title else _title
        description = title if not _description else _description

        filename = "_".join(title.lower().strip().split()) + ".md"
        path_file = os.path.join(self._base_data_path, filename)

        file_metadata = {
            "path": path_file,
            "url": response.url,
            "title": title,
            "description": description,
            "has_media": len(metadata.get("media", [])) if self._media else False
        }

        with open(path_file, "w") as f:
            mkdwn: str = self.__parse_markdown(result=response, fit=self._fit_markdown)

            f.write(mkdwn)

        return file_metadata

    def _update_links_queue(self, links: None | dict):
        """
        Updates the Queue with the next links to crawl
        """
        if not links:
            return

        _internal = links.get("internal")

        if not _internal:
            return

        for link in _internal:
            if isinstance(link, dict):
                url = link.get("href")
            else:
                url = link

            if not url or not isinstance(url, str):
                continue

            url = url.split("#")[0]
            self.queue.add(url)

    async def crawl(self):
        
        # TODO: Docstring
        # TODO: Implement media

        async with AsyncWebCrawler(browser_config=self.browser_config) as _crawler:
            while not self.queue.empty():
                url_to_fetch = self.queue.pop()

                if self.verbose:
                    logging.info(f"Fetching {url_to_fetch}, {len(self.queue)} links left.")

                result = await _crawler.arun(
                    url=url_to_fetch,
                    config=self.crawler_config,
                )

                if not result.success:
                    raise RuntimeError(f"""Something went wrong on Crawler Stage.\n\n{result.error_message}""")

                self._save_file(response=result)
                self._update_links_queue(links=result.links)
