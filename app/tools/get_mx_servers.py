import aiodns
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
        return -1
