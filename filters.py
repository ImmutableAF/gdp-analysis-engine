def filterByContinent(df, newCont):
    return df[df["Continent"] == newCont]

def filterByCountry(df, newCount):
    return df[df["Country Name"] == newCount]

def getYearColumns(df):
    return [col for col in df.columns if col.isdigit()]

def filterYearRange(df, startYear, endYear):
    yearColumns = [
        col for col in df.columns
        if col.isdigit() and startYear <= int(col) <= endYear
    ]
    staticCol = [col for col in df.columns if not col.isdigit()]

    return df[staticCol + yearColumns]

def filterBySpecificYear(df, year):
    year = str(year)
    if year not in df.columns:
        raise ValueError(f"Year {year} not found in DataTable.")
    staticCol = [col for col in df.columns if not col.isdigit()]
    return df[staticCol + [year]]

def filterByColumn(df, column, value):
    return df[df[column] == value]