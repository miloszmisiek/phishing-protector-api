import asyncio
import re
import aiofiles
from app.services.logger import logger


semaphore = asyncio.Semaphore(100)

async def count_tld(text):
    count = 0
    domain = text.split("//")[-1].split("/")[0].split('?')[0].split('#')[0]
    tld_part = domain.split('.')[-1].lower()
    async with aiofiles.open("app/services/tlds.txt", 'r') as file:
        async for line in file:
            clean_line = line.strip().lower()  # Ensure no newlines or spaces
            if clean_line == '.' + tld_part:
                count += 1
    return count


async def check_tld(query):
    """Check for presence of Top-Level Domains (TLD) in query params asynchronously."""
    async with semaphore:  # Acquire a semaphore slot
        # Read TLDs from file into a list
        tlds = []
        async with aiofiles.open("app/services/tlds.txt", 'r') as file:
            async for line in file:
                tlds.append(line.strip().lower())
        # Regex to find TLDs in the query
        tld_pattern = r"\b(" + "|".join(map(re.escape, tlds)) + r")\b"
        pattern = re.compile(tld_pattern)
        if pattern.search(query.lower()):
            logger.info(f"[check_tld] Matched TLD: {pattern.search(query.lower()).group()}")
            return 1
        else:
            logger.warning(f"check_tld] No TLD found for query: {query}")
    return 0


async def is_url_shortened(domain):
    """Check if the domain is a shortener asynchronously."""
    async with semaphore:
        logger.info(f"[is_url_shortened] Checking shorted url for {domain}")
        async with aiofiles.open('app/services/shorteners.txt', 'r') as file:
            async for line in file:
                with_www = "www." + line.strip()
                if line.strip() == domain.lower() or with_www == domain.lower():
                    return 1
    return 0
