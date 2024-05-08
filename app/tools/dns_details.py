import os
import certifi
import motor.motor_asyncio
from aiolimiter import AsyncLimiter
import aiodns
from datetime import datetime
from bson.json_util import dumps
from decouple import config

# load the configuration
DB_URI = config("DB_URI")

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
    DB_URI, tlsCAFile=certifi.where())
database = mongo_client.securityData
dns_collection = database.dnsRecords

limiter = AsyncLimiter(1, 1)


def default_serializer(obj):
    """Handle serialization of objects that JSON cannot serialize natively."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type not serializable: {type(obj).__name__}")


async def get_dns_details(domain):
    """Performs DNS queries for a given domain using cached data if available."""
    resolver = aiodns.DNSResolver()
    try:
        dns_data = await dns_collection.find_one({"domain": domain})
        if dns_data:
            print(f"Using mongo DNS data for {domain}")
            txt_records = dns_data.get('TXT', [])
            is_spf = 0
            for record in txt_records:
                if isinstance(record, str):
                    if 'v=spf1' in record.lower():
                        is_spf = 1
                        break
            mx_count = dns_data.get('MX', 0)
            ns_count = dns_data.get('NS', 0)
            ttl_num = dns_data.get('A', [])
            print(f"TXT records for {domain}: {txt_records}")
            print(f"MX records for {domain}: {mx_count}")
            print(f"NS records for {domain}: {ns_count}")
            return (is_spf, mx_count, ns_count, ttl_num[0] if len(ttl_num) else 0)
        else:
            async with limiter:
                print(f"Querying DNS data for {domain}")
                result_dict = {domain: {}}
                try:
                    # TXT records
                    txt_records = await resolver.query(domain, 'TXT')
                    txt_data = [record.text.decode('utf-8') if isinstance(record.text, bytes) else record.text
                                for record in txt_records]
                    is_spf = 0
                    for record in txt_data:
                        if isinstance(record, str):
                            if 'v=spf1' in record.lower():
                                is_spf = 1
                                break
                    result_dict[domain]['TXT'] = txt_data

                    # MX records
                    mx_records = await resolver.query(domain, 'MX')
                    print(f"MX records for {domain}: {len(mx_records)}")
                    result_dict[domain]['MX'] = len(mx_records)
                    mx_count = len(mx_records)

                    # NS records
                    ns_records = await resolver.query(domain, 'NS')
                    print(f"NS records for {domain}: {len(ns_records)}")
                    result_dict[domain]['NS'] = len(ns_records)
                    ns_count = len(ns_records)

                    # TTL records
                    ttl_records = await resolver.query(domain, 'A')
                    result_dict[domain]['A'] = [
                        record.ttl for record in ttl_records]
                    print(
                        f"TTL records for {domain}: {result_dict[domain]['A']}")
                    ttl_num = result_dict[domain]['A'][0]

                    # Cache the results
                    result = await dns_collection.insert_one({"domain": domain, **result_dict[domain]})
                    print(
                        f"Cached DNS data for {domain}: {result.inserted_id}")

                    return (is_spf, mx_count, ns_count, ttl_num if ttl_num else 0)

                except aiodns.error.DNSError as e:
                    print(f"Error querying in dns details {domain}: {e}")
                    result_dict[domain]['error'] = str(e)
                    # dns_data[domain] = result_dict[domain]
                    return (0, 0, 0, 0)
                except Exception as e:
                    print(
                        f"Unexpected error querying from dns details {domain}: {e}")
                    result_dict[domain]['error'] = str(e)
                    # dns_data[domain] = result_dict[domain]
                    return (0, 0, 0, 0)
    except Exception as e:
        print(f"Error querying cached DNS data for {domain}: {e}")
        return (0, 0, 0, 0)
