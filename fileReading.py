import pandas as pd

def readCSVfile(filename):
    try:
        df = pd.read_csv(filename)
        return df
    except FileNotFoundError:
        print(f"[ERROR]: File '{filename}' not found.")
    except pd.errors.EmptyDataError:
        print(f"[ERROR]: File '{filename}' is empty.")
    except pd.errors.ParserError:
        print(f"[ERROR]: File '{filename}' couldn't be parsed.")
    except Exception as e:
        print(f"[ERROR]: An unexpected error occurred: {e}")