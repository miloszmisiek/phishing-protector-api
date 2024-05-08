import ipaddress
import tldextract
from urllib.parse import urlparse

def is_domain_ip_address(url):
    """
    Check if the domain of a URL is in IP address format.

    :param url: The URL to check.
    :return: True if the domain is an IP address, False otherwise.
    """
    try:
        # Extract the domain or IP address part from the URL
        extracted = tldextract.extract(url)
        domain_or_ip = extracted.domain
        
        # In cases where the URL is directly an IP address, tldextract might not work as expected
        # So we also try parsing the netloc part directly
        parsed_url = urlparse(url)
        netloc = parsed_url.netloc
        
        # Attempt to create an IP address object from the domain
        # If this succeeds, the domain is an IP address
        if domain_or_ip:
            ipaddress.ip_address(domain_or_ip)
            return True
        else:
            # Attempt to handle cases where URL is directly an IP address
            ipaddress.ip_address(netloc.split(':')[0])  # Remove port number if present
            return True
    except ValueError:
        # If ValueError is raised, the domain is not in IP address format
        return False