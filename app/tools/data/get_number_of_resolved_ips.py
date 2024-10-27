import socket
import asyncio
from app.services.logger import logger

async def get_number_of_resolved_ips(domain):
    try:
        # Resolve the domain to its IP addresses
        # getaddrinfo returns a list of 5-tuples, but IPs are part of interest, which are the first element of the last tuple.
        resolved_info = await asyncio.get_event_loop().run_in_executor(None, socket.getaddrinfo, domain, None)
        logger.info(f"[get_number_of_resolved_ips] Resolved IPs for {domain}: {resolved_info}")
        # Extract unique IP addresses
        unique_ips = {info[4][0] for info in resolved_info}
        # Return the count of unique IP addresses
        return len(unique_ips)
    except Exception as e:
        logger.error(f"[get_number_of_resolved_ips] Error resolving ips for {domain}: {e}")
        return -1