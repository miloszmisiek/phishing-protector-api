import asyncio
import asyncwhois
import tldextract
from datetime import datetime
from pprint import pprint

from tools.async_files_functions import write_error

async def get_domain_expiration_in_days(domain):
    try:
        # Use asyncwhois for asynchronous WHOIS query
        _, parsed_dict = await asyncwhois.aio_whois(domain)
        expiration_date = parsed_dict.get('expires')
        # pprint(expiration_date)
        if expiration_date:
            # Ensure the expiration_date is aware of timezone for comparison
            if expiration_date.tzinfo is None:
                expiration_date = expiration_date.replace(tzinfo=datetime.now().astimezone().tzinfo)
            days_until_expiration = (expiration_date - datetime.now().astimezone()).days
            return days_until_expiration
        else:
            return None
    except Exception as e:
        print(f"Error processing {domain} by aio_whois in get_domain_expiration_in_days: {e}")
        await write_error(f"Error processing {domain} by aio_whois in get_domain_expiration_in_days: {e}")
        return None
async def process_domains_for_expiration(urls):
    # Extract the domain from each URL
    domains = [f"{tldextract.extract(url).domain}.{tldextract.extract(url).suffix}" for url in urls]
    
    # Create a task for each domain to get days until expiration
    tasks = [get_domain_expiration_in_days(domain) for domain in domains]
    results = await asyncio.gather(*tasks)
    return results