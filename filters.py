def filterByContinent(df, newCont):

    return df[df["Continent"] == newCont]

def filterByCountry(df, newCount):
    
    return df[df["Country Name"] == newCount]

def getYearColumns(df):
    
    return list(filter(str.isdigit(), df.columns))

def filterYearRange(df, startYear, endYear):
    cols = [
        col for col in df.columns
        if not col.isdigit() or startYear <= int(col) <= endYear
    ]
    return df[cols]

def filterBySpecificYear(df, year):
    year = str(year)
    if year not in df.columns:
        raise ValueError(f"Year {year} not found in DataTable.")
    
    staticCol = getYearColumns(df)
    return df[staticCol + [year]]

def filterByColumn(df, column, value):
    
    return df[df[column] == value]