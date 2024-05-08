import asyncio
import re
import aiofiles
import tldextract

semaphore = asyncio.Semaphore(100)

PATH = '/Users/miloszmisiek/Desktop/zut/magisterka/machine_learning/services/'

async def write_error(message):
    """Utility function to write error messages to a file."""
    async with aiofiles.open(PATH + 'errors.txt', 'a') as error_file:
        await error_file.write(message + '\n')

async def count_tld(text):
    count = 0
    domain = text.split("//")[-1].split("/")[0].split('?')[0].split('#')[0]
    tld_part = domain.split('.')[-1].lower()
    async with aiofiles.open(PATH + "tlds.txt", 'r') as file:
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
        async with aiofiles.open(PATH + "tlds.txt", 'r') as file:
            async for line in file:
                tlds.append(line.strip().lower())
        # Regex to find TLDs in the query
        tld_pattern = r"\b(" + "|".join(map(re.escape, tlds)) + r")\b"
        pattern = re.compile(tld_pattern)
        if pattern.search(query.lower()):
            print(f"Matched TLD: {pattern.search(query.lower()).group()}")
            return 1
        else:
            print(f"No TLD found for query: {query}")
            await write_error(f"No TLD found for query: {query}")
    return 0


async def is_url_shortened(domain):
    """Check if the domain is a shortener asynchronously."""
    async with semaphore:
        print(f"Checking shorted url for {domain}")
        async with aiofiles.open(PATH + 'shorteners.txt', 'r') as file:
            async for line in file:
                with_www = "www." + line.strip()
                if line.strip() == domain.lower() or with_www == domain.lower():
                    return 1
    return 0

async def process_domains_is_url_shortened(urls):
    # Extract the domain from each URL
    domains = [f"{tldextract.extract(url).domain}.{tldextract.extract(url).suffix}" for url in urls]
    # Create a task for each domain to check if it's a shortened URL
    tasks = [is_url_shortened(domain) for domain in domains]
    # Wait for all tasks to complete and return their results
    return await asyncio.gather(*tasks)