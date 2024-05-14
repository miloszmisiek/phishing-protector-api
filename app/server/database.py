import certifi
import motor.motor_asyncio
import asyncio
import pandas as pd
import tldextract
from app.tools.check_twitter_url import check_twitter_link
from app.tools.extract_features import extract_features
import joblib
from decouple import config

# load the configuration
DB_URI=config("DB_URI")

# constants
columns_to_drop = ['url', 'asn', 'qty_and_domain', 'qty_asterisk_domain', 'qty_asterisk_path', 'qty_asterisk_query', 'qty_asterisk_url', 'qty_at_domain', 'qty_comma_domain', 'qty_dollar_domain', 'qty_dollar_path', 'qty_equal_domain', 'qty_exclamation_domain',
                   'qty_hashtag_domain', 'qty_hashtag_path', 'qty_hashtag_query', 'qty_percent_domain', 'qty_plus_domain', 'qty_questionmark_domain', 'qty_questionmark_path', 'qty_slash_domain', 'qty_space_domain', 'qty_tilde_domain', 'qty_tilde_query', 'qty_underline_domain']

# Load the model
model = joblib.load("app/server/XGBoostClassifier-best-model.pickle.dat")

# connect to the MongoDB database
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
    DB_URI, tlsCAFile=certifi.where())
database = mongo_client.securityData
dns_collection = database.dnsRecords

# helpers


async def extract_features_for_all(urls: list):
    tasks = [extract_features(url) for url in urls]
    return await asyncio.gather(*tasks)


async def check_for_whitelisted_domain(url: str):
    extracted = tldextract.extract(url)
    domain = f"{extracted.domain}.{extracted.suffix}"
    result = await database.whitelist.find_one({'domain': domain})
    return result


async def check_for_blacklisted_domain(url: str):
    extracted = tldextract.extract(url)
    domain = f"{extracted.domain}.{extracted.suffix}"
    result = await database.blacklist.find_one({'domain': domain})
    return result


async def predict_model(urls: list):
    print(f"Predicting for {urls}")
    urls = [check_twitter_link(url) for url in urls]
    predictions = {}
    for url in urls:
        whitelisted = await check_for_whitelisted_domain(url)
        blacklisted = await check_for_blacklisted_domain(url)

        if whitelisted:
            predictions[url] = 0.0
        elif blacklisted:
            predictions[url] = 1.0
        else:
            feature_data = await extract_features_for_all([url])
            features_df = pd.DataFrame(feature_data)
            features_df = features_df.reindex(
                sorted(features_df.columns), axis=1)
            features_df.drop(columns_to_drop, axis=1, inplace=True)
            prediction_probas = model.predict_proba(features_df)
            positive_class_proba = prediction_probas[:, 1][0]
            predictions[url] = float(positive_class_proba)

    return {'predictions': predictions}


async def add_to_whitelist(urls: list):
    results = []
    for url in urls:
        url = check_twitter_link(url)
        try:
            extracted = tldextract.extract(url)
            domain = f"{extracted.domain}.{extracted.suffix}"

            # Check if the domain is in the blacklist and remove it
            if await database.blacklist.find_one({'domain': domain}):
                await database.blacklist.delete_one({'domain': domain})
                results.append({domain: 'Removed from blacklist'})

            # Check if the domain already exists in the whitelist
            existing_domain = await database.whitelist.find_one({'domain': domain})
            if existing_domain:
                results.append({domain: 'Already exists in whitelist'})
            else:
                # Insert the domain if it does not exist in whitelist
                await database.whitelist.insert_one({'domain': domain})
                results.append({domain: 'Added to whitelist'})

        except Exception as e:
            results.append({url: 'Failed'})

    return {'results': results}


async def add_to_blacklist(urls: list):
    results = []
    for url in urls:
        url = check_twitter_link(url)
        try:
            extracted = tldextract.extract(url)
            domain = f"{extracted.domain}.{extracted.suffix}"

            # Check if the domain is in the whitelist and remove it
            if await database.whitelist.find_one({'domain': domain}):
                await database.whitelist.delete_one({'domain': domain})
                results.append({domain: 'Removed from whitelist'})

            # Check if the domain already exists in the blacklist
            existing_domain = await database.blacklist.find_one({'domain': domain})
            if existing_domain:
                results.append({domain: 'Already exists in blacklist'})
            else:
                # Insert the domain if it does not exist in blacklist
                await database.blacklist.insert_one({'domain': domain})
                results.append({domain: 'Added to blacklist'})

        except Exception as e:
            results.append({url: 'Failed'})

    return {'results': results}