from urllib import parse
from urllib.parse import parse_qs, urlparse
import aiohttp
import tldextract
from tools.check_redirection import check_redirects
from tools.dns_details import get_dns_details
from tools.domains_details import get_domain_details
from tools.async_files_functions import check_tld, count_tld, is_url_shortened
from tools.check_blacklists import google_safebrowsing
from tools.get_number_of_resolved_ips import get_number_of_resolved_ips
from services.constants import CHARS_LEXICAL, KEYWORDS
from tools.get_asn_from_ip import get_asn_number
from tools.is_email_in_url import is_email_in_url
from tools.contains_keywords import contains_keywords
from tools.is_domain_ip_address import is_domain_ip_address
from tools.count_vowels import count_vowels
from tools.count_chars import count_chars


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
        features.update(count_chars(component_value,
                        CHARS_LEXICAL, component_name))

    domain_details = await get_domain_details(domain)
    dns_details = await get_dns_details(domain)

    async with aiohttp.ClientSession() as session:
        redirect_count = await check_redirects(url, session)

    # Additional features can be directly added to the dictionary
    features['length_url'] = len(url)
    features['https'] = 1 if url.startswith('https') else 0
    features['domain_in_ip'] = 1 if is_domain_ip_address(url) else 0
    features['qty_vowels_domain'] = count_vowels(domain)
    features['server_client_domain'] = 1 if contains_keywords(
        url, KEYWORDS) else 0
    features['qty_params'] = len(params_dict.keys())
    features['email_in_url'] = 1 if is_email_in_url(url) else 0
    if domain_details:
        print('domain_details', domain_details)
        features['time_domain_activation'] = domain_details[0]
        features['time_domain_expiration'] = domain_details[1]
    if dns_details:
        print('dns_details', dns_details)
        features['domain_spf'] = dns_details[0]
        features['qty_mx_servers'] = dns_details[1]
        features['qty_nameservers'] = dns_details[2]
        features['ttl_hostname'] = dns_details[3]
    features['qty_ip_resolved'] = await get_number_of_resolved_ips(domain)
    features['url_shortened'] = await is_url_shortened(domain)
    features['google_safe_browsing'] = await google_safebrowsing(url)
    features['tld'] = await check_tld(query) if query else 0
    features['qty_tls'] = await count_tld(url)
    features['asn'] = await get_asn_number(host)
    features['redirect_count'] = redirect_count

    return features