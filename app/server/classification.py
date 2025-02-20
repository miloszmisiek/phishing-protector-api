import asyncio
import pandas as pd
import tldextract
from app.server import database
from app.tools.data.check_twitter_url import check_twitter_link
from app.tools.data.extract_features import extract_features
from app.services.constants import COLUMNS_TO_DROP
import joblib

# Load the model
# model = joblib.load("app/server/xgb_model_43k_optimized.pickle.dat")
model = joblib.load("app/server/xgb_20250216_205143.pickle.dat")

# Methods to interact with the database
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


async def predict_single_url(url: str):
    whitelisted = await check_for_whitelisted_domain(url)
    blacklisted = await check_for_blacklisted_domain(url)

    if whitelisted:
        return url, 0.0
    elif blacklisted:
        return url, 1.0
    else:
        feature_data = await extract_features_for_all([url])
        features_df = pd.DataFrame(feature_data)
        features_df = features_df.reindex(sorted(features_df.columns), axis=1)
        features_df.drop(["url"], axis=1, inplace=True)
        prediction_probas = model.predict_proba(features_df)
        positive_class_proba = prediction_probas[:, 1][0]
        return url, float(positive_class_proba)

async def predict_model(urls: list):
    print(f"Predicting for {urls}")
    urls = [check_twitter_link(url) for url in urls]
    
    # Process all URLs concurrently
    results = await asyncio.gather(*[predict_single_url(url) for url in urls])
    
    # Convert results to dictionary
    return dict(results)

async def url_features(urls: list):
    print(f"Extracting features for {urls}")
    urls = [check_twitter_link(url) for url in urls]
    
    # Extract features for all URLs concurrently
    feature_data = await extract_features_for_all(urls)
    features_df = pd.DataFrame(feature_data)
    features_df = features_df.reindex(sorted(features_df.columns), axis=1)
    
    # Convert to dictionary list
    return features_df.to_dict(orient='records')


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
