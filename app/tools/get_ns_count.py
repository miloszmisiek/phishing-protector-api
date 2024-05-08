import asyncio
import aiodns
import tldextract

from tools.async_files_functions import write_error

async def get_ns_count(domain):
    resolver = aiodns.DNSResolver()
    try:
        # Perform an asynchronous query for NS records
        ns_records = await resolver.query(domain, 'NS')
        # Return the count of resolved NS records
        return len(ns_records)
    except Exception as e:
        print(f"Error querying NS records for {domain}: {e}")
        await write_error(f"Error querying NS records for {domain}: {e}")
        return None

async def process_domains_ns_count(urls):
    domains = [f"{tldextract.extract(url).domain}.{tldextract.extract(url).suffix}" for url in urls]
    # Create a task for each domain to get NS count
    tasks = [get_ns_count(domain) for domain in domains]
    # Await all tasks and collect results
    ns_counts = await asyncio.gather(*tasks)
    return ns_counts