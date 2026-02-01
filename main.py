import fileCleaning
import fileReading
import filters
import inputs
import statisticalOperations

filename = "gdp_with_continent_filled.csv"
df = fileReading.readCSVfile(filename)


if df is not None:
    df = fileCleaning.cleanFile(df)
while True:
    user_inputs = inputs.getFilterInputs()

    if user_inputs["choice"] == "1":
        df_filtered = filters.filterByContinent(df, user_inputs["continent"])
    elif user_inputs["choice"] == "2":
        df_filtered = filters.filterByCountry(df, user_inputs["country"])
    elif user_inputs["choice"] == "3":
        df_filtered = filters.filterBySpecificYear(df, user_inputs["year"])
    elif user_inputs["choice"] == "4":
        df_filtered = filters.filterYearRange(df, user_inputs["startYear"], user_inputs["endYear"])
    elif user_inputs["choice"] == "5":
        df_filtered = df
    print(df_filtered)
