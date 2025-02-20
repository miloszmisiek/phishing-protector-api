from enum import Enum

CHARS_LEXICAL = {
    '.': 'dot',
    '-': 'hyphen',
    '_': 'underline',
    '/': 'slash',
    '?': 'questionmark',
    '=': 'equal',
    '@': 'at',
    '&': 'and',
    '!': 'exclamation',
    ' ': 'space',
    '~': 'tilde',
    ',': 'comma',
    '+': 'plus',
    '*': 'asterisk',
    '#': 'hashtag',
    '$': 'dollar',
    '%': 'percent'
}
KEYWORDS = ["server", "client"]

COLUMNS_TO_SELECT = ['https', 'is_email_in_url', 'is_server_client_in_domain', 'is_shortened_url', 'is_spf_domain', 'is_tld_in_query_params', 'length_url', 'qty_and_path', 'qty_and_query', 'qty_and_url', 'qty_asterisk_query', 'qty_asterisk_url', 'qty_at_path', 'qty_at_query', 'qty_at_url', 'qty_comma_path', 'qty_comma_query', 'qty_comma_url', 'qty_dollar_path', 'qty_dollar_query', 'qty_dollar_url', 'qty_dot_domain', 'qty_dot_path', 'qty_dot_query', 'qty_dot_url', 'qty_equal_path', 'qty_equal_query', 'qty_equal_url', 'qty_hashtag_url', 'qty_hyphen_domain', 'qty_hyphen_path', 'qty_hyphen_query', 'qty_hyphen_url', 'qty_ip_resolved', 'qty_mx_servers', 'qty_nameservers', 'qty_params', 'qty_percent_path', 'qty_percent_query', 'qty_percent_url', 'qty_plus_query', 'qty_plus_url', 'qty_questionmark_query', 'qty_questionmark_url', 'qty_slash_path', 'qty_slash_query', 'qty_slash_url', 'qty_space_path', 'qty_space_query', 'qty_space_url', 'qty_tilde_path', 'qty_tilde_query', 'qty_tilde_url', 'qty_tld', 'qty_underline_path', 'qty_underline_query', 'qty_underline_url', 'qty_vowels_domain', 'redirect_count', 'time_domain_activation', 'time_domain_expiration', 'ttl_hostname']

COLUMNS_TO_DROP = ['url', 'qty_and_domain', 'qty_asterisk_domain', 'qty_asterisk_path', 'qty_at_domain', 'qty_comma_domain', 'qty_dollar_domain', 'qty_equal_domain', 'qty_exclamation_domain',
                   'qty_hashtag_domain', 'qty_hashtag_path', 'qty_hashtag_query', 'qty_plus_domain', 'qty_questionmark_domain', 'qty_questionmark_path', 'qty_slash_domain', 'qty_space_domain', 'qty_tilde_domain', 'qty_underline_domain']

WHOIS_FIELDS_TO_NORMALIZE = ['created', 'creation_date', 'creationdate', 'registryCreationDate',
                             'expires', 'expiration_date', 'registryExpiryDate', 'updated', 'updated_date']


class AuthKeys(str, Enum):
    SECRET = "AUTH_SECRET_KEY"
    ALGORITHM = "ALGORITHM"
    DB_URI = "DB_URI"


class ExceptionMessages(str, Enum):
    INVALID_CREDENTIALS = "Could not validate credentials"
    INACTIVE_USER = "Inactive user"
