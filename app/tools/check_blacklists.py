import aiohttp
import certifi
import ssl

from decouple import config

async def google_safebrowsing(url):
    client_id = config("GOOGLE_SAFE_BROWSING_CLIENT_ID")
    version = config("GOOGLE_SAFE_BROWSING_VERSION")
    api_key = config("GOOGLE_SAFE_BROWSING_API_KEY")
    platform_types = ['ANY_PLATFORM']
    threat_types = ['THREAT_TYPE_UNSPECIFIED', 'MALWARE', 'SOCIAL_ENGINEERING',
                    'UNWANTED_SOFTWARE', 'POTENTIALLY_HARMFUL_APPLICATION']
    threat_entry_types = ['URL']
    api_url = f'https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}'
    threat_entries = [{'url': url}]
    payload = {
        'client': {
            'clientId': client_id,
            'clientVersion': version
        },
        'threatInfo': {
            'threatTypes': threat_types,
            'platformTypes': platform_types,
            'threatEntryTypes': threat_entry_types,
            'threatEntries': threat_entries
        }
    }
    headers = {'Content-Type': 'application/json'}

    sslcontext = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl_context=sslcontext)

    async with aiohttp.ClientSession(connector=conn) as session:
        try:
            async with session.post(api_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    responseData = await response.json()
                    print(f"Google Safebrowsing API response: {responseData}")
                    return 1 if responseData else 0
                else:
                    print(f"Failed to query Google Safebrowsing API for {url}")
                    return -1
        except Exception as e:
            print(f"Error querying Google Safebrowsing API for {url}: {e}")
            return -1
