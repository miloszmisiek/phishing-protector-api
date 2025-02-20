import asyncwhois
import whois
from datetime import datetime, timezone
from app.services.constants import WHOIS_FIELDS_TO_NORMALIZE
from app.services.logger import logger
from app.server.database import domain_collection


def to_isoformat(date):
    """Converts datetime objects or lists of them to a string in ISO format."""
    if not date:
        return None

    if isinstance(date, list):
        # Ensure all items are datetime objects, then select the earliest
        date = min(datetime.fromisoformat(str(d))
                   if isinstance(d, str) else d for d in date)

    if isinstance(date, datetime):
        # Add UTC timezone if missing
        return date.replace(tzinfo=timezone.utc).isoformat() if date.tzinfo is None else date.isoformat()

    return date


def to_datetime(date):
    """Converts strings or lists of dates to offset-aware datetime objects."""
    if isinstance(date, list):
        date = min(datetime.fromisoformat(str(d))
                   if isinstance(d, str) else d for d in date)
    elif isinstance(date, str):
        date = datetime.fromisoformat(date)
    if date.tzinfo is None:  # Add UTC if timezone info is missing
        date = date.replace(tzinfo=timezone.utc)
    return date


def normalize_whois_data(whois_dict):
    """ Normalizes the WHOIS data dictionary by converting all datetime objects to ISO format strings. """
    return {
        key: to_isoformat(value) if key in WHOIS_FIELDS_TO_NORMALIZE else value
        for key, value in whois_dict.items()
    }


async def get_domain_details(domain):
    logger.info(
        f"[get_domain_details] Processing {domain} in get_domain_details")
    try:
        # Check MongoDB for existing data
        domain_data = await domain_collection.find_one({"domain": domain})
        parsed_dict = None
        if domain_data:
            logger.info(
                f"[get_domain_details] Using WHOIS data for {domain} from MongoDB")
            creation_date = domain_data.get('created')
            expiration_date = domain_data.get('expires')
            parsed_dict = domain_data
            logger.debug(
                f"[get_domain_details] MongoDB creation_date: {creation_date}, expiration_date: {expiration_date}")
        else:
            try:
                # Try async WHOIS query
                logger.info(
                    f"[get_domain_details] Running async WHOIS for {domain}")
                _, parsed_dict = await asyncwhois.aio_whois(domain)
                creation_date = parsed_dict.get('created')
                expiration_date = parsed_dict.get('expires')
                logger.debug(
                    f"[get_domain_details] Async WHOIS result for {domain}: {parsed_dict}")
            except Exception as async_error:
                logger.error(
                    f"[get_domain_details] Async WHOIS failed for {domain}: {async_error}")
                try:
                    # Fallback to RDAP lookup using whodap
                    logger.info(
                        f"[get_domain_details] Attempting RDAP lookup for {domain}")
                    _, parsed_dict = asyncwhois.rdap(domain)
                    logger.debug(
                        f"[get_domain_details] RDAP result for {domain}: {parsed_dict}")
                    creation_date = parsed_dict.get('created')
                    expiration_date = parsed_dict.get('expires')
                    logger.debug(
                        f"[get_domain_details] RDAP creation_date: {creation_date}, expiration_date: {expiration_date}")
                except Exception as rdap_error:
                    logger.exception(
                        f"[get_domain_details] RDAP lookup failed for {domain}: {rdap_error}")
                    try:
                        # Final fallback to sync whois
                        logger.info(
                            f"[get_domain_details] Falling back to sync WHOIS for {domain}")
                        parsed_dict = whois.whois(domain)
                        creation_date = parsed_dict.creation_date
                        expiration_date = parsed_dict.expiration_date
                        logger.debug(
                            f"[get_domain_details] Sync WHOIS result for {domain}: {parsed_dict}")
                        logger.debug(
                            f"[get_domain_details] Sync creation_date: {creation_date}, expiration_date: {expiration_date}")
                    except Exception as sync_error:
                        logger.exception(
                            f"[get_domain_details] Sync WHOIS failed for {domain}: {sync_error}")
                        creation_date = None
                        expiration_date = None

        logger.debug(
            f"[get_domain_details] Parsed_dict before saving: {parsed_dict}")
        if parsed_dict:
            try:
                normalized_data = normalize_whois_data(parsed_dict)
                logger.debug(
                    f"[get_domain_details] Normalized WHOIS data: {normalized_data}")
                await domain_collection.replace_one(
                    {"domain": domain}, {"domain": domain, **normalized_data}, upsert=True
                )
                logger.info(
                    f"[get_domain_details] Successfully saved WHOIS data for {domain}")
            except Exception as e:
                logger.exception(
                    f"[get_domain_details] Failed to save data for {domain}: {e}")
        else:
            logger.warning(
                f"[get_domain_details] Parsed_dict is empty or None for {domain}. Skipping save.")

        current_time = datetime.now().astimezone()
        logger.debug(f"[get_domain_details] Current time: {current_time}")
        creation_timestamp, expiration_timestamp = None, None

        # Normalize creation_date
        if creation_date:
            logger.debug(
                f"[get_domain_details] Raw creation_date before conversion: {creation_date}")
            creation_date = to_datetime(creation_date)  # Ensure timezone-aware
            logger.debug(
                f"[get_domain_details] Converted creation_date: {creation_date}")
            creation_timestamp = creation_date.timestamp()
            logger.info(
                f"[get_domain_details] Domain {domain} creation timestamp: {creation_timestamp}")

        # Normalize expiration_date
        if expiration_date:
            logger.debug(
                f"[get_domain_details] Raw expiration_date before conversion: {expiration_date}")
            expiration_date = to_datetime(expiration_date)  # Ensure timezone-aware
            logger.debug(
                f"[get_domain_details] Converted expiration_date: {expiration_date}")
            expiration_timestamp = expiration_date.timestamp()
            logger.info(
                f"[get_domain_details] Domain {domain} expiration timestamp: {expiration_timestamp}")

        return creation_timestamp or 0, expiration_timestamp or 0

    except Exception as e:
        logger.exception(
            f"[get_domain_details] Unknown error processing {domain}: {e}")
        return 0, 0
