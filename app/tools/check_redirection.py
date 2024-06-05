import aiohttp
from aiolimiter import AsyncLimiter
from colorama import Fore

limiter = AsyncLimiter(1, 1)

async def check_redirects(url, session):
    try:
        async with limiter:
            async with session.get(url, ssl=False) as response:
                print(Fore.GREEN + f"Checking redirects for {url}")
                return len(response.history)
    except aiohttp.TooManyRedirects as e:
        return len(e.history)
    except Exception as e:
        print(Fore.RED + f"Error during redirect check for {url}: {e}")
        return -1