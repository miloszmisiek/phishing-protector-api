import socket
import asyncio
import tldextract

from tools.async_files_functions import write_error

async def get_number_of_resolved_ips(domain):
    try:
        # Resolve the domain to its IP addresses
        # getaddrinfo returns a list of 5-tuples, but we're only interested in the IPs, which are the first element of the last tuple.
        resolved_info = await asyncio.get_event_loop().run_in_executor(None, socket.getaddrinfo, domain, None)
        print(f"Resolved IPs for {domain}: {resolved_info}")
        # Extract unique IP addresses
        unique_ips = {info[4][0] for info in resolved_info}
        # Return the count of unique IP addresses
        return len(unique_ips)
    except Exception as e:
        print(f"Error resolving ips for {domain}: {e}")
        await write_error(f"Error resolving ips for {domain}: {e}")
        return -1
    
async def process_domains(urls):
    # Extract the domain from each URL
    domains = [f"{tldextract.extract(url).domain}.{tldextract.extract(url).suffix}" for url in urls]
    
    # Create a task for each domain
    tasks = [get_number_of_resolved_ips(domain) for domain in domains]
    results = await asyncio.gather(*tasks)
    return results