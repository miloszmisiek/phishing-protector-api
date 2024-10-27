import geoip2.database
import ipaddress
import asyncio
import aiodns

def valid_ip(host):
    """Check if the domain has a valid IP format (IPv4 or IPv6)."""
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False
    

async def get_asn_number(host):
    """Async return of the ASN number associated with the IP."""
    resolver = aiodns.DNSResolver()
    print(f"Getting ASN for {host}")
    
    try:
        if valid_ip(host):
            ip = host
        else:
            response = await resolver.query(host, 'A')
            ip = response[0].host

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, read_asn_number, ip)
        return response
    except Exception as e:
        print(f"Error processing asn for {host}: {e}")
        return -1

def read_asn_number(ip):
    """Synchronously reads ASN number using geoip2."""
    with geoip2.database.Reader('app/services/GeoLite2-ASN.mmdb') as reader:
        response = reader.asn(ip)
        return response.autonomous_system_number
