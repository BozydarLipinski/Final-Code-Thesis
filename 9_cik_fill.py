import pandas as pd


def add_mapping_row(df, cik, cusip6, cusip8):
    new_row = pd.DataFrame([{
        'cik': cik,
        'cusip6': cusip6,
        'cusip8': cusip8
    }])
    return pd.concat([df, new_row], ignore_index=True)


df = pd.read_csv("cusip.csv", dtype=str)

df = add_mapping_row(df, "1131399", "37733W", "37733W10")
df = add_mapping_row(df, "105729", "950817", "95081710")
df = add_mapping_row(df, "1156039", "49773V", "49773V10")
df = add_mapping_row(df, "1156039", "949773", "949773V10")
df = add_mapping_row(df, "1699150", "G47766", "G4776610")
df = add_mapping_row(df, "800921", "641069", "64106940")

df.to_csv("cusip_V1.csv", index=False)