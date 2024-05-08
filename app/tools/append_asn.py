# import pandas as pd
# import asyncio
# # from tools.get_asn_from_ip import get_asn_from_domain_async
# import tldextract

# # Load the existing data
# output_file_path = '/Users/miloszmisiek/Desktop/zut/magisterka/machine_learning/output_features.csv'
# phishtank_csv = "/Users/miloszmisiek/Desktop/zut/magisterka/machine_learning/verified_online.csv"
# df_existing = pd.read_csv(output_file_path)

# # Print the first few rows to verify it's loaded correctly
# print(df_existing.head())


# async def append_asn_to_dataframe(df):
#     asn_tasks = [get_asn_from_domain_async(tldextract.extract(url).registered_domain) for url in df['url']]
#     asn_results = await asyncio.gather(*asn_tasks)
    
#     # Add the ASN results to the DataFrame
#     df['asn'] = asn_results

# async def update_csv_with_asn():
#     df = pd.read_csv(output_file_path)  # Load the existing data
#     df1 = pd.read_csv(phishtank_csv) 
#     await append_asn_to_dataframe(df1)  # Append ASN information
#     df.to_csv(output_file_path, index=False)  # Save the updated DataFrame

# # Run the update
# if __name__ == "__main__":
#     asyncio.run(update_csv_with_asn())
