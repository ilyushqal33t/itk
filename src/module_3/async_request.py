import asyncio
import aiohttp
import json
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_single_url(
    session: aiohttp.ClientSession, url: str, semaphore: asyncio.Semaphore
) -> Dict[str, int]:
    async with semaphore:
        try:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                return {"url": url, "status_code": response.status}

        except asyncio.TimeoutError:
            logger.warning(f"Timeout for {url}")
            return {"url": url, "status_code": 0}

        except aiohttp.ClientConnectorError:
            logger.warning(f"Connection error for {url}")
            return {"url": url, "status_code": 0}

        except aiohttp.ServerDisconnectedError:
            logger.warning(f"Server disconnected for {url}")
            return {"url": url, "status_code": 0}

        except aiohttp.ClientResponseError as e:
            logger.warning(f"Client response error for {url}: {e}")
            return {"url": url, "status_code": e.status if e.status else 0}

        except aiohttp.InvalidURL:
            logger.warning(f"Invalid URL {url}")
            return {"url": url, "status_code": 0}

        except Exception as e:
            logger.warning(f"Error for {url}: {e}")
            return {"url": url, "status_code": 0}


async def fetch_url(urls: list[str], file_path: str) -> Dict[str, int]:
    semaphore = asyncio.Semaphore(5)
    results = {}

    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = asyncio.create_task(fetch_single_url(session, url, semaphore))
            tasks.append(task)

        url_results = await asyncio.gather(*tasks)

        with open(file_path, "w", encoding="utf-8") as f:
            for result in url_results:
                url = result["url"]
                status_code = result["status_code"]
                results[url] = status_code

                json_line = json.dumps(
                    {"url": url, "status_code": status_code}, ensure_ascii=False
                )
                f.write(json_line + "\n")

    logger.info(f"Results saved to {file_path}")
    return results


async def main():
    urls = [
        "https://example.com",
        "https://httpbin.org/status/404",
        "https://nonexistent.url",
    ]

    await fetch_url(urls, "./results.json")


if __name__ == "__main__":
    asyncio.run(main())
