import aiodns
from app.services.logger import logger

async def get_mx_count(domain):
    resolver = aiodns.DNSResolver()
    try:
        # Perform an asynchronous query for MX records
        mx_records = await resolver.query(domain, 'MX')
        # Return the count of MX records
        return len(mx_records)
    except Exception as e:
        logger.error(f"Error querying MX records in get_mx_count for {domain}: {e}")
        return -1
