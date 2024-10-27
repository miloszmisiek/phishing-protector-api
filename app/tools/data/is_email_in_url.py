import re

def is_email_in_url(url):
    """
    Search for an email address within a URL.

    :param url: The URL string to search.
    :return: The first found email address, or None if no email address is found.
    """
    # Regular expression pattern for matching email addresses
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    
    # Search for email addresses in the URL
    match = re.search(email_pattern, url)
    
    # Return the found email address, if any
    return match.group(0) if match else None