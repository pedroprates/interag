import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import CrawlerRunConfig, BrowserConfig, CacheMode

URL = "https://workable.readme.io/reference/generate-an-access-token"

async def main():
    browser_config = BrowserConfig(verbose=True)
    crawler_config = CrawlerRunConfig(
        word_count_threshold=10,
        exclude_external_links=True,
        remove_overlay_elements=True,
        process_iframes=True,
        excluded_tags=["form"],
        cache_mode=CacheMode.ENABLED,
    )

    async with AsyncWebCrawler(browser_config=browser_config) as crawler:
        result = await crawler.arun(
            url=URL,
            config=crawler_config,
        )

        response.metadata["title"].
        with open("output.md", "w") as f:
            mkdwn = result.markdown

            if type(mkdwn) is str:
                f.write(mkdwn)

                print(result.links["internal"])

if __name__ == "__main__":
    asyncio.run(main())
