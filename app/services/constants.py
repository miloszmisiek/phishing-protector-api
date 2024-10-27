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

COLUMNS_TO_DROP = ['url', 'asn', 'qty_and_domain', 'qty_asterisk_domain', 'qty_asterisk_path', 'qty_asterisk_query', 'qty_asterisk_url', 'qty_at_domain', 'qty_comma_domain', 'qty_dollar_domain', 'qty_dollar_path', 'qty_equal_domain', 'qty_exclamation_domain',
                   'qty_hashtag_domain', 'qty_hashtag_path', 'qty_hashtag_query', 'qty_percent_domain', 'qty_plus_domain', 'qty_questionmark_domain', 'qty_questionmark_path', 'qty_slash_domain', 'qty_space_domain', 'qty_tilde_domain', 'qty_tilde_query', 'qty_underline_domain']

WHOIS_FIELDS_TO_NORMALIZE = ['created', 'creation_date', 'creationdate', 'registryCreationDate',
                             'expires', 'expiration_date', 'registryExpiryDate', 'updated', 'updated_date']


class AuthKeys(str, Enum):
    SECRET = "SECRET_KEY"
    ALGORITHM = "ALGORITHM"
    DB_URI = "DB_URI"


class ExceptionMessages(str, Enum):
    INVALID_CREDENTIALS = "Could not validate credentials"
    INACTIVE_USER = "Inactive user"
