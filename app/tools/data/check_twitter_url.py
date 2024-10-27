import requests


def check_twitter_link(url: str) -> str:
    return url if not url.startswith('https://t.co/') else requests.head(url, allow_redirects=True).url
