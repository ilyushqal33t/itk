import asyncio
import aiohttp
import json
from typing import List, Dict
from pathlib import Path
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
                content = None
                if response.status == 200:
                    try:
                        content = await response.json()
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON for {url}")

                return {"url": url, "status_code": response.status, "content": content}

        except asyncio.TimeoutError:
            logger.warning(f"Timeout for {url}")
            return {"url": url, "status_code": 0, "content": None}

        except aiohttp.ClientConnectorError:
            logger.warning(f"Connection error for {url}")
            return {"url": url, "status_code": 0, "content": None}

        except aiohttp.ServerDisconnectedError:
            logger.warning(f"Server disconnected for {url}")
            return {"url": url, "status_code": 0, "content": None}

        except aiohttp.ClientResponseError as e:
            logger.warning(f"Client response error for {url}: {e}")
            return {
                "url": url,
                "status_code": e.status if e.status else 0,
                "content": None,
            }

        except aiohttp.InvalidURL:
            logger.warning(f"Invalid URL {url}")
            return {"url": url, "status_code": 0, "content": None}

        except Exception as e:
            logger.warning(f"Error for {url}: {e}")
            return {"url": url, "status_code": 0, "content": None}


async def read_urls_from_file(file_path: str) -> List[str]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"URLs file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    logger.info(f"Read {len(urls)} URLs from {file_path}")
    return urls


async def fetch_urls(input_file: str, output_file: str) -> None:
    urls = await read_urls_from_file(input_file)
    semaphore = asyncio.Semaphore(5)
    success_count = 0
    total_count = len(urls)

    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            task = asyncio.create_task(fetch_single_url(session, url, semaphore))
            tasks.append(task)

        url_results = await asyncio.gather(*tasks)

        with open(output_file, "w", encoding="utf-8") as f:
            for future in asyncio.as_completed(tasks):
                try:
                    result = await future

                    if result["status_code"] == 200 and result["content"] is not None:
                        json_line = json.dumps(
                            {"url": result["url"], "content": result["content"]},
                            ensure_ascii=False,
                        )
                        f.write(json_line + "\n")
                        success_count += 1

                    if total_count % 100 == 0:
                        logger.info(
                            f"Processed {total_count}/{len(urls)} URLs, {success_count} successful"
                        )

                except Exception as e:
                    logger.error(f"Error:{e}")

    logger.info(
        f"Processed {total_count} URLs, {success_count} successful. Saved to {output_file}"
    )


async def main():
    await fetch_urls("test_urls.txt", "result.json")


if __name__ == "__main__":
    asyncio.run(main())
