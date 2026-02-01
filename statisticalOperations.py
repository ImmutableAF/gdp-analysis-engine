import filters

# average of gdp of region

def find_averageGDP_by_region_overall(df, region):
    df_filtered = filters.filterByContinent(df, str(region))
    year_cols = filters.getYearColumns(df_filtered)

    return df_filtered[year_cols].mean()

def find_averageGDP_by_region_rangeOfYears(df, region, from_year, till_year):
    df_filtered = filters.filterByContinent(df, str(region))
    df_filtered = filters.filterYearRange(df_filtered, from_year, till_year)
    year_cols = filters.getYearColumns(df_filtered)

    return df_filtered[year_cols].mean()


def find_averageGDP_by_region_specificYear(df, region, year):
    df_filtered = filters.filterByContinent(df, str(region))

    return df_filtered[str(year)].mean()

# average of gdp of country

def find_averageGDP_of_country_overall(df, countryname):
    df_filtered = filters.filterByCountry(df, str(countryname))
    year_cols = filters.getYearColumns(df_filtered)

    return df_filtered[year_cols].values.mean()

def find_averageGDP_of_country_rangeOfYears(df, countryname, from_year, till_year):
    df_filtered = filters.filterByCountry(df, str(countryname))
    df_filtered = filters.filterYearRange(df_filtered, from_year, till_year)
    year_cols = filters.getYearColumns(df_filtered)

    return df_filtered[year_cols].values.mean()

def find_averageGDP_of_country_specificYear(df, countryname, year):
    df_filtered = filters.filterByCountry(df, str(countryname))

    return df_filtered[str(year)].mean()

# sum of gdp of regions

def find_sum_of_GDPs_overall(df, region):
    df_filtered = filters.filterByContinent(df, str(region))
    year_cols = filters.getYearColumns(df_filtered)

    return df_filtered[year_cols].sum()

def find_sum_of_GDPs_rangeOfYears(df, region, from_year, till_year):
    df_filtered = filters.filterByContinent(df, str(region))
    df_filtered = filters.filterYearRange(df_filtered, from_year, till_year)
    year_cols = filters.getYearColumns(df_filtered)
    
    return df_filtered[year_cols].sum()

def find_sum_of_GDPs_specificYear(df, region, year):
    df_filtered = filters.filterByContinent(df, str(region))
    
    return df_filtered[str(year)].sum()