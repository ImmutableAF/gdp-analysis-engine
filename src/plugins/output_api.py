"""
Output Analytics API
====================

A FastAPI application that exposes GDP analytics as REST endpoints.
Proxies requests to the Core API (running on port 8010) and returns
JSON responses.

Base URL: ``http://localhost:8010``

Endpoints
---------
- ``GET /top-countries`` — Top N countries by GDP for a given continent and year.
- ``GET /bottom-countries`` — Bottom N countries by GDP.
- ``GET /gdp-growth-rate`` — Year-on-year GDP growth rate per country.
- ``GET /avg-gdp-by-continent`` — Average GDP grouped by continent.
- ``GET /global-gdp-trend`` — Total global GDP summed per year.
- ``GET /fastest-growing-continent`` — Continents ranked by GDP growth over a period.
- ``GET /consistent-decline`` — Countries with consistent GDP decline over X years.
- ``GET /continent-gdp-share`` — Each continent's share of global GDP as a percentage.
"""

import httpx
import pandas as pd
import orjson
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import Response

CORE_API_URL = "http://localhost:8010"
ALL_REGIONS = "__ALL__"

app = FastAPI(title="GDP Analytics API")


def _json(df: pd.DataFrame) -> Response:
    """Serialize a DataFrame to a JSON HTTP response using orjson.

    Parameters
    ----------
    df : pd.DataFrame
        The data to serialize.

    Returns
    -------
    Response
        A FastAPI response with ``application/json`` media type.
    """
    return Response(
        content=orjson.dumps(
            df.to_dict(orient="records"), option=orjson.OPT_SERIALIZE_NUMPY
        ),
        media_type="application/json",
    )


def _fetch(path: str, payload: dict) -> pd.DataFrame:
    """POST a query to the Core API and return the result as a DataFrame.

    Parameters
    ----------
    path : str
        The Core API endpoint path, e.g. ``/run``.
    payload : dict
        The JSON body to send.

    Returns
    -------
    pd.DataFrame
        Parsed response data.

    Raises
    ------
    httpx.HTTPStatusError
        If the Core API returns a non-2xx status.
    """
    with httpx.Client() as client:
        r = client.post(f"{CORE_API_URL}{path}", json=payload, timeout=30)
        r.raise_for_status()
        return pd.DataFrame(r.json())


@app.get("/top-countries")
def top_countries(
    continent: str = Query(...), year: int = Query(...), n: int = Query(10)
):
    """Return the top N countries by GDP for a given continent and year.

    Parameters
    ----------
    continent : str
        Continent name to filter by.
    year : int
        The year to query.
    n : int
        Number of countries to return. Defaults to 10.
    """
    df = _fetch("/run", {"region": continent, "startYear": year, "endYear": year})
    result = (
        df.groupby("Country Name")["Value"]
        .sum()
        .nlargest(n)
        .reset_index()
        .rename(columns={"Country Name": "country", "Value": "gdp"})
    )
    return _json(result)


@app.get("/bottom-countries")
def bottom_countries(
    continent: str = Query(...), year: int = Query(...), n: int = Query(10)
):
    """Return the bottom N countries by GDP for a given continent and year.

    Parameters
    ----------
    continent : str
        Continent name to filter by.
    year : int
        The year to query.
    n : int
        Number of countries to return. Defaults to 10.
    """
    df = _fetch("/run", {"region": continent, "startYear": year, "endYear": year})
    result = (
        df.groupby("Country Name")["Value"]
        .sum()
        .nsmallest(n)
        .reset_index()
        .rename(columns={"Country Name": "country", "Value": "gdp"})
    )
    return _json(result)


@app.get("/gdp-growth-rate")
def gdp_growth_rate(
    continent: str = Query(...), startYear: int = Query(...), endYear: int = Query(...)
):
    """Return year-on-year GDP growth rate (%) per country for a continent.

    Parameters
    ----------
    continent : str
        Continent name to filter by.
    startYear : int
        First year of the range.
    endYear : int
        Last year of the range.
    """
    df = _fetch(
        "/run", {"region": continent, "startYear": startYear, "endYear": endYear}
    )
    yearly = (
        df.groupby(["Country Name", "Year"])["Value"]
        .sum()
        .unstack("Year")
        .sort_index(axis=1)
    )
    growth = yearly.pct_change(axis=1, fill_method=None).iloc[:, 1:] * 100
    result = (
        growth.reset_index()
        .melt(id_vars="Country Name", var_name="year", value_name="growth_rate_pct")
        .dropna()
        .rename(columns={"Country Name": "country"})
    )
    return _json(result)


@app.get("/avg-gdp-by-continent")
def avg_gdp_by_continent(startYear: int = Query(...), endYear: int = Query(...)):
    """Return average GDP grouped by continent over a year range.

    Parameters
    ----------
    startYear : int
        First year of the range.
    endYear : int
        Last year of the range.
    """
    df = _fetch(
        "/run", {"region": ALL_REGIONS, "startYear": startYear, "endYear": endYear}
    )
    result = (
        df.groupby("Continent")["Value"]
        .mean()
        .reset_index()
        .rename(columns={"Continent": "continent", "Value": "avg_gdp"})
    )
    return _json(result)


@app.get("/global-gdp-trend")
def global_gdp_trend(startYear: int = Query(...), endYear: int = Query(...)):
    """Return total global GDP summed per year over a range.

    Parameters
    ----------
    startYear : int
        First year of the range.
    endYear : int
        Last year of the range.
    """
    df = _fetch(
        "/run", {"region": ALL_REGIONS, "startYear": startYear, "endYear": endYear}
    )
    result = (
        df.groupby("Year")["Value"]
        .sum()
        .reset_index()
        .rename(columns={"Year": "year", "Value": "total_gdp"})
    )
    return _json(result)


@app.get("/fastest-growing-continent")
def fastest_growing_continent(startYear: int = Query(...), endYear: int = Query(...)):
    """Return continents ranked by GDP growth percentage between two years.

    Parameters
    ----------
    startYear : int
        Base year for growth calculation.
    endYear : int
        End year for growth calculation.

    Raises
    ------
    HTTPException
        400 if either year is not present in the data.
    """
    df = _fetch(
        "/run", {"region": ALL_REGIONS, "startYear": startYear, "endYear": endYear}
    )
    boundary = df[df["Year"].isin([startYear, endYear])]
    pivoted = boundary.groupby(["Continent", "Year"])["Value"].sum().unstack("Year")

    if startYear not in pivoted.columns or endYear not in pivoted.columns:
        raise HTTPException(
            status_code=400, detail="startYear or endYear not found in data"
        )

    pivoted["growth_pct"] = (
        (pivoted[endYear] - pivoted[startYear]) / pivoted[startYear]
    ) * 100
    result = (
        pivoted[["growth_pct"]]
        .reset_index()
        .rename(columns={"Continent": "continent"})
        .sort_values("growth_pct", ascending=False)
    )
    return _json(result)


@app.get("/consistent-decline")
def consistent_decline(lastXYears: int = Query(...), referenceYear: int = Query(...)):
    """Return countries that have shown consistent GDP decline over the last X years.

    Parameters
    ----------
    lastXYears : int
        Number of consecutive years of decline to check for.
    referenceYear : int
        The most recent year in the decline window.
    """
    start = referenceYear - lastXYears - 1
    df = _fetch(
        "/run", {"region": ALL_REGIONS, "startYear": start, "endYear": referenceYear}
    )
    yearly = (
        df.groupby(["Country Name", "Year"])["Value"]
        .sum()
        .unstack("Year")
        .sort_index(axis=1)
    )

    def all_declining(row):
        vals = row.dropna().values
        return len(vals) == lastXYears and all(
            vals[i] > vals[i + 1] for i in range(len(vals) - 1)
        )

    def avg_decline_pct(row):
        vals = row.dropna().values
        pct_changes = [
            (vals[i + 1] - vals[i]) / vals[i] * 100 for i in range(len(vals) - 1)
        ]
        return sum(pct_changes) / len(pct_changes)

    mask = yearly.apply(all_declining, axis=1)
    result = yearly[mask].apply(avg_decline_pct, axis=1).reset_index()
    result.columns = ["country", "avg_decline_pct"]
    result = result.sort_values("avg_decline_pct")
    return _json(result)


@app.get("/continent-gdp-share")
def continent_gdp_share(startYear: int = Query(...), endYear: int = Query(...)):
    """Return each continent's share of global GDP as a percentage.

    Parameters
    ----------
    startYear : int
        First year of the range.
    endYear : int
        Last year of the range.
    """
    df = _fetch(
        "/run", {"region": ALL_REGIONS, "startYear": startYear, "endYear": endYear}
    )
    continent_total = df.groupby("Continent")["Value"].sum()
    global_total = continent_total.sum()
    result = (
        (continent_total / global_total * 100)
        .reset_index()
        .rename(columns={"Continent": "continent", "Value": "share_pct"})
        .sort_values("share_pct", ascending=False)
    )
    return _json(result)
