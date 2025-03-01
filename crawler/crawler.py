import os
import json
import re
import shutil
import random
import logging
import requests
from crawl4ai import AsyncWebCrawler
from crawl4ai.models import CrawlResult, MarkdownGenerationResult
from crawl4ai.async_configs import CrawlerRunConfig, BrowserConfig, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawler.queue import URLQueue

__all__ = ["Crawler"]

logger = logging.getLogger(__name__)

class Crawler:
    """Crawler class responsible to crawl the URL and all the internal links referenced on it"""

    def __init__(
        self,
        url: str,
        media: bool = False,
        verbose: bool = True,
        fit_markdown: bool = False,
        clean: bool = True,
        remove_tags: None | list[str] = ["form", "nav", "header"],
        cache: bool = False,
    ):
        self._url = url
        self._media = media
        self.verbose = verbose
        self._fit_markdown = fit_markdown
        self._base_data_path = "data"
        self._pages_path = "pages"
        self._media_path = "media"
        self._remove_tags = remove_tags
        self._cache = cache
        
        # Only while all media types are not implemented yet
        self._media_warn = False

        if clean and os.path.exists(self._base_data_path):
            shutil.rmtree(self._base_data_path)

        crawler_ops = {
            "word_count_threshold": 10,
            "exclude_external_links": True,
            "remove_overlay_elements": True,
            "process_iframes": True,
            "excluded_tags": self._remove_tags,
            "cache_mode": CacheMode.ENABLED if self._cache else CacheMode.DISABLED,
        }

        if self._fit_markdown:
            _prune_filter = PruningContentFilter(
                threshold=.45,
                threshold_type="dynamic",
                min_word_threshold=5,
            )

            _md_generator = DefaultMarkdownGenerator(content_filter=_prune_filter)

            crawler_ops["markdown_generator"] = _md_generator

        self.browser_config = BrowserConfig(verbose=self.verbose)
        self.crawler_config = CrawlerRunConfig(**crawler_ops)
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

        title = re.sub(r"[^a-zA-Z0-9]", "", title)
        filename = "_".join(title.lower().strip().split()) + ".md"
        path = os.path.join(self._base_data_path, self._pages_path)

        os.makedirs(path, exist_ok=True)

        path_file = os.path.join(path, filename)

        file_metadata = {
            "path": path_file,
            "url": response.url,
            "title": title,
            "description": description,
            "has_media": len(metadata.get("media", [])) if self._media else False
        }

        mkdwn: str = self.__parse_markdown(result=response, fit=self._fit_markdown)

        if mkdwn:
            with open(path_file, "w") as f:
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

    def _save_media(self, media: dict | list[dict], page_name: str):
        """
        Download and save media files from the crawler, this function should only be called when `media` parameter
        is set to `True`.

        It is going to be saved inside a subfolder media inside the base crawling folder.

        Currently only images are available

        Args:
            media (dict | list[dict]): the media variable from the CrawlerResult
            page_name (str): page name that the crawler sent the media from
        """
        if not self._media_warn:
            logging.warning("Only Images are available to download, Audio and Videos are not yet implemented")
            self._media_warn = True

        if isinstance(media, dict):
            media = media["images"]

        for file in media:
            url = file["src"]

            file_response = requests.get(url)

            if file_response.status_code == 200:
                filename = url.split("/")[-1]
                page_name = "_".join(page_name.lower().strip().split())
                path = os.path.join(self._base_data_path, self._media_path, page_name)

                os.makedirs(path, exist_ok=True)

                filepath = os.path.join(path, filename)

                with open(filepath, "wb") as file:
                    file.write(file_response.content)

            else:
                logging.error(f"Failed to download image from {url}")


    async def crawl(self):
        """
        Crawling from the base page to last page.

        Receives a base URL, crawl the base URL always adding the new URLs found to the Queue to achieve crawling from the entire site.

        Queue is a unique Queue, avoiding to crawl duplicates.
        """
        
        metadata = []

        async with AsyncWebCrawler(browser_config=self.browser_config) as _crawler:
            while not self.queue.empty():
                try:
                    url_to_fetch = self.queue.pop()
                except IndexError:
                    break
                except:
                    raise

                if self.verbose:
                    logging.info(f"Fetching {url_to_fetch}")

                result = await _crawler.arun(
                    url=url_to_fetch,
                    config=self.crawler_config,
                )

                if not result.success:
                    raise RuntimeError(f"""Something went wrong on Crawler Stage.\n\n{result.error_message}""")

                file_metadata = self._save_file(response=result)
                metadata.append(file_metadata)
                self._update_links_queue(links=result.links)

                if self._media:
                    self._save_media(
                        media=result.media, page_name=file_metadata.get("title", "")
                    )

        metadata_path = os.path.join(self._base_data_path, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=4)

        logging.info(f"Completed! Crawled {len(self.queue.seen)} files.")
