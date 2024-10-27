import certifi
import motor.motor_asyncio
from app.services.constants import AuthKeys
from decouple import config

# Load the configuration
DB_URI = config(AuthKeys.DB_URI.value)

# Connect to the MongoDB database
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
    DB_URI, tlsCAFile=certifi.where())
database = mongo_client.securityData
dns_collection = database.dnsRecords
user_collection = database.user
domain_collection = database.whoisRecords

