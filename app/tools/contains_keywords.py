import tldextract

def contains_keywords(url, keywords):
    """
    Check if the domain of a URL contains any of the specified keywords.

    :param url: The URL to check.
    :param keywords: A list of keywords to look for in the domain.
    :return: True if any keyword is found in the domain, False otherwise.
    """
    # Extract the domain from the URL
    extracted = tldextract.extract(url)
    domain = f"{extracted.domain}.{extracted.suffix}"
    
    # Alternatively, for simple use cases, you might directly work with the netloc part from urlparse
    # netloc = urlparse(url).netloc

    # Check if any of the keywords are in the domain
    return any(keyword in domain for keyword in keywords)