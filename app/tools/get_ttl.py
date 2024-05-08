import asyncio
import aiodns
import tldextract

from tools.async_files_functions import write_error

async def get_ttl_of_hostname(hostname):
    resolver = aiodns.DNSResolver()
    try:
        # Perform an asynchronous query for A records to get IPv4 addresses
        # For IPv6 addresses, change 'A' to 'AAAA'
        a_records = await resolver.query(hostname, 'A')
        if a_records:
            # Assuming we're interested in the TTL of the first A record
            ttl = a_records[0].ttl
            return ttl
        else:
            return None  # No A records found
    except Exception as e:
        print(f"Error querying A records for {hostname} (ttl): {e}")
        await write_error(f"Error querying A records for {hostname} (ttl): {e}")
        return None  # Return None if there's an error

async def process_hostnames_for_ttl(urls):
    # Extract the domain from each URL
    hostnames = [f"{tldextract.extract(url).domain}.{tldextract.extract(url).suffix}" for url in urls]
    # Create a task for each hostname to get its TTL
    tasks = [get_ttl_of_hostname(hostname) for hostname in hostnames]
    # Await all tasks and collect results
    ttl_values = await asyncio.gather(*tasks)
    return ttl_values