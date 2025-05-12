from sec_api import Form13FHoldingsApi
import pandas as pd


# Initialize the API client
api_key = '47a1a9f434370c6b078b1a2adad0375d44e22632d0032ef566257f0ca579dc4e'  # You need to replace this with your actual API key
query_api = Form13FHoldingsApi(api_key)

# Set the CIK for Berkshire Hathaway
cik = '1067983'  # This is the CIK for Berkshire Hathaway

# Define the query parameters for scraping the filings
query = {
    "query": f"cik:{cik} AND formType:\"13F-HR\"",
    "from": "50",
    "size": "20",  # Number of results to fetch, adjust based on your needs
    "sort": [{"filedAt": {"order": "desc"}}]  # Sort by filed date descending
}

# Run the query
response = query_api.get_data(query)


# Extract relevant data from the response
filings = response['data']
data = []
for filing in filings:
    filing_date = filing['periodOfReport']
    for holding in filing['holdings']:
        if "ticker" in holding:
            filing_data = {
                "cik": cik,
                "filedFor": filing_date,
                "ticker": holding["ticker"],
                "no_shares": holding["shrsOrPrnAmt"]["sshPrnamt"],
                "value": holding["value"],
                "nameOfIssuer": holding["nameOfIssuer"]
            }
            data.append(filing_data)

# Convert the data to a DataFrame
df = pd.DataFrame(data)

# Save the results to a CSV file
df.to_csv('berkshire_hathaway_portfolio_filings2.csv', index=False)

print("Data successfully saved to 'berkshire_hathaway_portfolio_filings2.csv'")