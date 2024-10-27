import aiodns

from app.services.logger import logger


async def check_spf_record_async(domain: str) -> bool:
    """
    Asynchronously check if the given domain has an SPF record in its DNS settings.

    :param domain: The domain to check.
    :return: True if an SPF record is found, False otherwise.
    """
    resolver = aiodns.DNSResolver()
    try:
        txt_records = await resolver.query(domain, 'TXT')
        for txt_record in txt_records:
            if txt_record.text.startswith('v=spf1'):
                return True
        return False
    except Exception as e:  # Catching a broad exception as aiodns can raise different exceptions based on the environment
        logger.error(f"Error querying SPF record for {domain}: {e}")        
        return False
