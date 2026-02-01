import fileCleaning
import fileReading
import filters

filename = "gdp_with_continent_filled.csv"
df = fileReading.readCSVfile(filename)


if df is not None:
    df = fileCleaning.cleanFile(df)
    #print(df.head())

df_filtered = filters.filterYearRange(df, 1997, 2000)
print(df_filtered)