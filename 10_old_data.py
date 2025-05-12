import pandas as pd
import requests
import re
import json
from datetime import datetime
import csv
import numpy as np

cusip = {}
cusip_mapping = pd.read_csv("holdings.csv", header=None)

with open('cusip_V1.csv', newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 2:  # make sure there's at least two columns
            cusip[row[2]] = row[0]


def remove_until_s(lines):
    for i, line in enumerate(lines):
        if line.lstrip().startswith("<S>"):
            return lines[i + 1:]  # skip the <S> line as well
    return []


# Function to parse a line with fixed-width columns
def parse_fixed_width(line, widths):
    cols = []
    idx = 0
    for width in widths:
        cols.append(line[idx:idx + width].strip())
        idx += width
    return cols


def get_all_txt_links():
    with open('index.json', 'r') as f:
        data = json.load(f)

    return [
        (filing['periodOfReport'], filing['linkToTxt'])
        for filing in data.get('filings', [])
        if 'linkToTxt' in filing and filing.get('formType') == '13F-HR'
    ]


def get_column_widths(block):
    positions = []
    for match in re.finditer(r"<[SC]>", block):
        positions.append(match.start())

    # Sort and compute distances (i.e., column widths)
    positions.sort()
    return [positions[i + 1] - positions[i] for i in range(len(positions) - 1)]


def get_cik(cusip_id):
    if cusip_id in cusip:
        return int(float(cusip[cusip_id]))
    return ""


def retrieve_data_from_url(url, filing_date):
    response = requests.get(url, headers=headers)
    content = response.text

    # Find all <table>...</table> blocks, skipping the first one
    table_blocks = re.findall(r'<TABLE>.*?</TABLE>', content, re.DOTALL | re.IGNORECASE)
    c_block_pattern = re.compile(r"(?:<C>(?:\s*<C>){4,})")
    table_blocks = [block for block in table_blocks if c_block_pattern.search(block)]


    if not table_blocks:
        return pd.DataFrame()

    data = pd.DataFrame()
    # Process each table block
    processed_rows = []
    for i, table in enumerate(table_blocks):
        lines = table.strip().splitlines()
        lines = remove_until_s(lines)
        for i, line in enumerate(lines):
            if '---' in line:
                lines = lines[:i]  # keep everything before this line
                break

        column_widths = get_column_widths(table)

        # Parse all lines into a dataframe
        parsed_data = [parse_fixed_width(row, column_widths) for row in lines]
        df = pd.DataFrame(parsed_data)
        data = pd.concat([data, df], ignore_index=True)

    for i in range(1, len(data)):
        if data.iloc[i, 2].strip() == "":
            data.iloc[i, 1] = data.iloc[i - 1, 1]
            data.iloc[i, 2] = data.iloc[i - 1, 2]

    mask = ~data.apply(lambda row: row.astype(str).str.contains('---|===')).any(axis=1) & data.iloc[:, 3].fillna(
        '').astype(str).str.strip().ne('')
    data = data[mask]

    try:
        data = data.iloc[:, [2, 3, 4]]
        data['filedFor'] = datetime.fromisoformat(filing_date).date()
        return data
    except:
        return pd.DataFrame()


def normalize_cusip(value):
    value = str(value).strip()

    if ' ' in value:
        parts = value.split()
        if len(parts) >= 2:
            first_part = parts[0]
            second_part = parts[1][:2]  # only first two characters

            if len(first_part) == 5:
                first_part = '0' + first_part  # pad a leading zero

            return first_part + second_part
        else:
            return value  # fallback if badly formatted
    else:
        return value[:8]


def get_ticker(cusip):
    row = cusip_mapping[cusip_mapping.iloc[:, 0] == cusip]
    if row.empty:
        return ""
    else:
        return row.iloc[0, 1]


# MAIN

pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', None)  # Disable line wrapping
pd.set_option('display.max_colwidth', None)  # Show full content in each cell

headers = {
    "User-Agent": "Your Name (your.email@example.com)",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov"
}

txt_links = get_all_txt_links()

all_dfs = []
for url in txt_links:
   data = retrieve_data_from_url(url[1], url[0])
   if not data.empty:
       print(url[0] + '    ' + url[1])
       all_dfs.append(data)

merged_df = pd.concat(all_dfs, ignore_index=True)
merged_df.iloc[:, 0] = merged_df.iloc[:, 0].apply(normalize_cusip)


merged_df.columns.values[0] = 'cupsid'
merged_df.columns.values[1] = 'valuation'
merged_df.columns.values[2] = 'shares'

for i in range(len(merged_df)):
    cupsid = merged_df.iloc[i]['cupsid']
    merged_df.at[i, 'cik'] = get_cik(cupsid)
    merged_df.at[i, 'ticker'] = get_ticker(cupsid)


merged_df = merged_df.replace("", np.nan)


merged_df.at[1940, 'valuation'] = merged_df.at[1940, 'valuation'].replace(" 1", "")
merged_df.at[1940, 'shares'] = '120,255,879'

merged_df.at[1954, 'valuation'] = merged_df.at[1954, 'valuation'].replace(" 1", "")
merged_df.at[1954, 'shares'] = '139,945,600'

merged_df.at[3448, 'valuation'] = merged_df.at[3448, 'valuation'].replace(" 1", "")
merged_df.at[3448, 'shares'] = '16,140,300'

merged_df.at[3469, 'valuation'] = merged_df.at[3469, 'valuation'].replace(" 1", "")
merged_df.at[3469, 'shares'] = '12,902,590'

merged_df.at[3457, 'valuation'] = merged_df.at[3457, 'valuation'].replace(" 2", "")
merged_df.at[3457, 'shares'] = '22,000,000'

merged_df.at[3474, 'valuation'] = merged_df.at[3474, 'valuation'].replace(" 3", "")
merged_df.at[3474, 'shares'] = '38,404,360'

merged_df = merged_df.dropna(subset=['shares'])

merged_df['filedFor'] = pd.to_datetime(merged_df['filedFor'], errors='coerce')

merged_df = merged_df[~merged_df['filedFor'].dt.year.isin([1998, 1999, 2000, 2001])]

merged_df = merged_df.reset_index(drop=True)

merged_df['valuation'] = merged_df['valuation'].astype(str).replace({'\\$': '', ',': ''}, regex=True)
merged_df['shares'] = merged_df['shares'].astype(str).replace({'\\$': '', ',': ''}, regex=True)

merged_df['cik'] = merged_df['cik'].astype(int)
merged_df['valuation'] = merged_df['valuation'].astype(int)
merged_df['shares'] = merged_df['shares'].astype(int)

merged_df.to_csv("all_data.csv", index=False)