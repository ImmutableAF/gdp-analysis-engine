import pandas as pd

def cleanFile(df):
    try:
        df.fillna(0, inplace=True)
        df.fillna("Unknown", inplace=True)
        return df
    except Exception as a:
        print(f"[ERROR]: Couldn't clean the file: {a}")