from time import clock_getres
from urllib import parse
from urllib.parse import parse_qs, urlparse
import aiohttp
import tldextract
from app.tools.data.check_redirection import check_redirects
from app.tools.data.dns_details import get_dns_details
from app.tools.data.domains_details import get_domain_details
from app.tools.data.async_files_functions import check_tld_in_query_params, count_tld, is_url_shortened
from app.tools.data.check_blacklists import google_safebrowsing
from app.tools.data.get_number_of_resolved_ips import get_number_of_resolved_ips
from app.services.constants import CHARS_LEXICAL, COLUMNS_TO_SELECT, KEYWORDS
from app.tools.data.is_email_in_url import is_email_in_url
from app.tools.data.contains_keywords import contains_keywords
from app.tools.data.is_domain_ip_address import is_domain_ip_address
from app.tools.data.count_vowels import count_vowels
from app.tools.data.count_chars import count_chars


def start_url(url):
    """Split URL into: protocol, host, path, params, query and fragment."""
    if not parse.urlparse(url.strip()).scheme:
        url = 'http://' + url
    protocol, host, path, params, query, fragment = parse.urlparse(url.strip())

    result = {
        'url': host + path + params + query + fragment,
        'protocol': protocol,
        'host': host,
        'path': path,
        'params': params,
        'query': query,
        'fragment': fragment
    }
    return result


async def extract_features(url):    
    features = {}
    parsed_url = urlparse(url)
    extracted = tldextract.extract(url)
    domain = f"{extracted.domain}.{extracted.suffix}"
    path = parsed_url.path
    query = parsed_url.query
    host = parsed_url.netloc
    params_dict = parse_qs(query)

    # Dictionary of URL components to apply the count_chars function
    url_components = {
        'url': url,
        'domain': domain,
        'path': path,
        'query': query
    }
    features['url'] = url
    # Apply count_chars to each URL component
    for component_name, component_value in url_components.items():
        char_counts = count_chars(component_value, CHARS_LEXICAL, component_name)
        for feature_name, value in char_counts.items():
            if feature_name in COLUMNS_TO_SELECT:
                features[feature_name] = value

    domain_details = await get_domain_details(domain)
    dns_details = await get_dns_details(domain)

    async with aiohttp.ClientSession() as session:
        redirect_count = await check_redirects(url, session)

    # Additional features can be directly added to the dictionary
    features['length_url'] = len(url)
    features['https'] = 1 if url.startswith('https') else 0
    # features['is_ip_in_domain'] = 1 if is_domain_ip_address(url) else 0
    features['qty_vowels_domain'] = count_vowels(domain)
    features['is_server_client_in_domain'] = 1 if contains_keywords(
        url, KEYWORDS) else 0
    features['qty_params'] = len(params_dict.keys())
    features['is_email_in_url'] = 1 if is_email_in_url(url) else 0
    if domain_details:
        features['time_domain_activation'] = domain_details[0]
        features['time_domain_expiration'] = domain_details[1]
    if dns_details:
        print('dns_details', dns_details)
        features['is_spf_domain'] = dns_details[0]
        features['qty_mx_servers'] = dns_details[1]
        features['qty_nameservers'] = dns_details[2]
        features['ttl_hostname'] = dns_details[3]
    features['qty_ip_resolved'] = await get_number_of_resolved_ips(domain)
    features['is_shortened_url'] = await is_url_shortened(domain)
    # features['google_safe_browsing'] = await google_safebrowsing(url)
    features['is_tld_in_query_params'] = await check_tld_in_query_params(query) if query else 0
    features['qty_tld'] = await count_tld(url)
    features['redirect_count'] = redirect_count

    return features