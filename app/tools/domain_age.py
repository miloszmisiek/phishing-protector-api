import asyncio
import asyncwhois
import whois
import tldextract
import json
from datetime import datetime, timezone
from tools.async_files_functions import write_error


async def get_domain_age_in_days(domain, whois_data, retries=3, backoff=1):
    if domain in whois_data:
        creation_date = whois_data[domain].get('created')
    else:
        creation_date = None
        try:
            while retries > 0:
                try:
                    # Use asyncwhois for asynchronous WHOIS query
                    _, parsed_dict = await asyncwhois.aio_whois(domain)
                    creation_date = parsed_dict.get('created')
                    if creation_date:
                        break
                except ConnectionResetError:
                    retries -= 1
                    if retries <= 0:
                        raise
                    await asyncio.sleep(backoff)
                    backoff *= 2  # Exponential backoff
        except Exception as e:
            print(f"Error with async WHOIS for {domain}: {e}")
            await write_error(f"Error with async WHOIS for {domain}: {e}")

        if not creation_date:  # If asyncwhois failed, fall back to synchronous whois
            try:
                result = whois.whois(domain)
                creation_date = result.creation_date
            except Exception as e:
                print(f"Error with synchronous WHOIS for {domain}: {e}")
                await write_error(f"Error with synchronous WHOIS for {domain}: {e}")

    if creation_date:
        if isinstance(creation_date, list):
            # Handle cases where whois returns multiple dates
            creation_date = creation_date[0]
        if creation_date.tzinfo is not None:
            creation_date = creation_date.astimezone(
                timezone.utc).replace(tzinfo=None)
        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        age_in_days = (current_time - creation_date).days
        return age_in_days
    return None


async def process_domains(urls):
    # Load the local WHOIS data
    try:
        with open("whois_results.json", 'r') as file:
            whois_data = json.load(file)
    except FileNotFoundError:
        whois_data = {}

    # Extract the domain from each URL
    domains = [
        f"{tldextract.extract(url).domain}.{tldextract.extract(url).suffix}" for url in urls]

    # Create a task for each domain
    tasks = [get_domain_age_in_days(domain, whois_data) for domain in domains]
    results = await asyncio.gather(*tasks)
    return results
