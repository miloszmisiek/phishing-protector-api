import aiodns
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
        return -1