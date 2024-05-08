import requests


def check_twitter_link(url):
    return url if not url.startswith('https://t.co/') else requests.head(url, allow_redirects=True).url
