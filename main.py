import fileCleaning
import fileReading

filename = "gdp_with_continent_filled.csv"


df = fileReading.readCSVfile(filename)
if df is not None:
    df = fileCleaning.cleanFile(df)
    print(df.head(15))