import aiohttp
from aiolimiter import AsyncLimiter
from colorama import Fore

from app.services.logger import logger

limiter = AsyncLimiter(1, 1)


async def check_redirects(url: str, session: aiohttp.ClientSession) -> int:
    try:
        async with limiter:
            async with session.get(url, ssl=False) as response:
                logger.info(f"Checking redirects for {url}")
                return len(response.history)
    except aiohttp.TooManyRedirects as e:
        return len(e.history)
    except Exception as e:
        logger.error(f"Error checking redirects for {url}: {e}")
        return -1
