import filters

def find_averageGDP_by_region_overall(df, region):
    df_filtered = filters.filterByContinent(df, str(region))

    year_cols = [col for col in df_filtered.columns if col.isdigit()]
    return df_filtered[year_cols].mean()

def find_averageGDP_by_region_rangeOfYears(df, region, from_year, till_year):
    df_filtered = filters.filterByContinent(df, str(region))
    df_filtered = filters.filterYearRange(df_filtered, from_year, till_year)

    year_cols = [col for col in df_filtered.columns if col.isdigit()]
    return df_filtered[year_cols].mean()


def find_averageGDP_by_region_specificYear(df, region, year):
    df_filtered = filters.filterByContinent(df, str(region))
    df_filtered = filters.filterBySpecificYear(df_filtered, str(year))

    return df_filtered[str(year)].mean()

def find_averageGDP_of_country_overall(df, countryname):
    df_filtered = filters.filterByCountry(df, str(countryname))

    year_cols = [col for col in df_filtered.columns if col.isdigit()]
    return df_filtered[year_cols].values.mean()

def find_averageGDP_of_country_rangeOfYears(df, countryname, from_year, till_year):
    df_filtered = filters.filterByCountry(df, str(countryname))
    df_filtered = filters.filterYearRange(df_filtered, from_year, till_year)

    year_cols = [col for col in df_filtered.columns if col.isdigit()]
    return df_filtered[year_cols].values.mean()

def find_averageGDP_of_country_specificYear(df, countryname, year):
    df_filtered = filters.filterByCountry(df, str(countryname))
    df_filtered = filters.filterBySpecificYear(df_filtered, str(year))

    return df_filtered[str(year)].mean()