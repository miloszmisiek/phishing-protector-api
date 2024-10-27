import asyncwhois
import whois
from datetime import datetime, timezone
from aiolimiter import AsyncLimiter
from decouple import config
from app.services.constants import WHOIS_FIELDS_TO_NORMALIZE, AuthKeys
from app.services.logger import logger
from app.server.database import domain_collection

# load the configuration
DB_URI = config(AuthKeys.DB_URI)
limiter = AsyncLimiter(1, 1)


def to_isoformat(date):
    """Converts datetime objects to a string in ISO format."""
    if not date:
        return None
    if isinstance(date, list):
        # Choose the earliest date if there are multiple, and ensure it is a datetime object
        date = min([datetime.fromisoformat(str(d))
                   if isinstance(d, str) else d for d in date])
    if isinstance(date, datetime):
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        return date.isoformat()
    return date  # Return as-is if it's already a string or another format that's not handled here


def normalize_whois_data(whois_dict):
    """ Normalizes the WHOIS data dictionary by converting all datetime objects to ISO format strings. """
    normalized = {}
    for key, value in whois_dict.items():
        if key in WHOIS_FIELDS_TO_NORMALIZE:
            normalized[key] = to_isoformat(value)
        else:
            normalized[key] = value
    return normalized


async def get_domain_details(domain):
    logger.info(f"Processing {domain} in get_domain_details")
    try:
        domain_data = await domain_collection.find_one({"domain": domain})
        if domain_data:
            logger.info(
                f"Using mongo WHOIS data for {domain} in get_domain_details")
            creation_date = domain_data.get('created')
            expiration_date = domain_data.get('expires')
        else:
            async with limiter:
                try:
                    # Asynchronous WHOIS query
                    logger.info(
                        f"Running async WHOIS for {domain} in get_domain_details")
                    _, parsed_dict = await asyncwhois.aio_whois(domain)
                    creation_date = parsed_dict.get('created')
                    expiration_date = parsed_dict.get('expires')
                except Exception as async_error:
                    logger.error(
                        f"Async WHOIS failed in get_domain_details for {domain}, attempting sync WHOIS: {async_error}")
                    # Fallback to synchronous whois
                    parsed_dict = whois.whois(domain)
                    creation_date = parsed_dict.creation_date
                    expiration_date = parsed_dict.expiration_date
            await domain_collection.insert_one({"domain": domain, **normalize_whois_data(parsed_dict)})
            logger.info(
                f"Normalizing WHOIS data for {domain}: {normalize_whois_data(parsed_dict)}")

        current_time = datetime.now().astimezone()
        age_in_days, days_until_expiration = 0, 0

        # Calculate domain age
        if creation_date:
            if isinstance(creation_date, list):
                creation_date = min([datetime.fromisoformat(str(date)) if isinstance(
                    date, str) else date for date in creation_date])
            elif isinstance(creation_date, str):
                creation_date = datetime.fromisoformat(creation_date)
            if creation_date.tzinfo is None:
                creation_date = creation_date.replace(tzinfo=timezone.utc)
            age_in_days = (current_time - creation_date).days

        # Calculate days until expiration
        if expiration_date:
            if isinstance(expiration_date, list):
                expiration_date = max([datetime.fromisoformat(str(date)) if isinstance(
                    date, str) else date for date in expiration_date])
            elif isinstance(expiration_date, str):
                expiration_date = datetime.fromisoformat(expiration_date)
            if expiration_date.tzinfo is None:
                expiration_date = expiration_date.replace(tzinfo=timezone.utc)
            days_until_expiration = (expiration_date - current_time).days

        return (age_in_days, days_until_expiration)

    except Exception as e:
        error_msg = f"Error processing {domain}: {e}"
        logger.error(error_msg)
        return (0, 0)
