import asyncio
import aiodns
import tldextract

from tools.async_files_functions import write_error

async def get_mx_count(domain):
    resolver = aiodns.DNSResolver()
    try:
        # Perform an asynchronous query for MX records
        mx_records = await resolver.query(domain, 'MX')
        # Return the count of MX records
        return len(mx_records)
    except Exception as e:
        print(f"Error querying MX records for {domain}: {e}")
        await write_error(f"Error querying MX records for {domain}: {e}")
        return None

async def process_domains_mx_count(urls):
    # Extract the domain from each URL
    domains = [f"{tldextract.extract(url).domain}.{tldextract.extract(url).suffix}" for url in urls]
    # Create a task for each domain to get MX count
    tasks = [get_mx_count(domain) for domain in domains]
    # Await all tasks and collect results
    mx_counts = await asyncio.gather(*tasks)
    return mx_counts