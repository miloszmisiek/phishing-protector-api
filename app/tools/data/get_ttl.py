import aiodns
from app.services.logger import logger


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
        logger.error(f"[get_ttl_of_hostname] Error querying A records for {hostname} (ttl): {e}")
        return None  # Return None if there's an error