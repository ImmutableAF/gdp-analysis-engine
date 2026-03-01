import httpx
import pandas as pd
import orjson
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import Response

CORE_API_URL = "http://localhost:8010"
ALL_REGIONS = "__ALL__"

app = FastAPI(title="GDP Analytics API")


def _json(df: pd.DataFrame) -> Response:
    return Response(
        content=orjson.dumps(df.to_dict(orient="records"), option=orjson.OPT_SERIALIZE_NUMPY),
        media_type="application/json",
    )


def _fetch(path: str, payload: dict) -> pd.DataFrame:
    with httpx.Client() as client:
        r = client.post(f"{CORE_API_URL}{path}", json=payload, timeout=30)
        r.raise_for_status()
        return pd.DataFrame(r.json())


@app.get("/top-countries")
def top_countries(continent: str = Query(...), year: int = Query(...), n: int = Query(10)):
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
def bottom_countries(continent: str = Query(...), year: int = Query(...), n: int = Query(10)):
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
def gdp_growth_rate(continent: str = Query(...), startYear: int = Query(...), endYear: int = Query(...)):
    df = _fetch("/run", {"region": continent, "startYear": startYear, "endYear": endYear})
    yearly = (
        df.groupby(["Country Name", "Year"])["Value"]
        .sum()
        .unstack("Year")
        .sort_index(axis=1)
    )
    growth = yearly.pct_change(axis=1).iloc[:, 1:] * 100
    result = (
        growth.reset_index()
        .melt(id_vars="Country Name", var_name="year", value_name="growth_rate_pct")
        .dropna()
        .rename(columns={"Country Name": "country"})
    )
    return _json(result)


@app.get("/avg-gdp-by-continent")
def avg_gdp_by_continent(startYear: int = Query(...), endYear: int = Query(...)):
    df = _fetch("/run", {"region": ALL_REGIONS, "startYear": startYear, "endYear": endYear})
    result = (
        df.groupby("Continent")["Value"]
        .mean()
        .reset_index()
        .rename(columns={"Continent": "continent", "Value": "avg_gdp"})
    )
    return _json(result)


@app.get("/global-gdp-trend")
def global_gdp_trend(startYear: int = Query(...), endYear: int = Query(...)):
    df = _fetch("/run", {"region": ALL_REGIONS, "startYear": startYear, "endYear": endYear})
    result = (
        df.groupby("Year")["Value"]
        .sum()
        .reset_index()
        .rename(columns={"Year": "year", "Value": "total_gdp"})
    )
    return _json(result)


@app.get("/fastest-growing-continent")
def fastest_growing_continent(startYear: int = Query(...), endYear: int = Query(...)):
    df = _fetch("/run", {"region": ALL_REGIONS, "startYear": startYear, "endYear": endYear})
    boundary = df[df["Year"].isin([startYear, endYear])]
    pivoted = boundary.groupby(["Continent", "Year"])["Value"].sum().unstack("Year")

    if startYear not in pivoted.columns or endYear not in pivoted.columns:
        raise HTTPException(status_code=400, detail="startYear or endYear not found in data")

    pivoted["growth_pct"] = ((pivoted[endYear] - pivoted[startYear]) / pivoted[startYear]) * 100
    result = (
        pivoted[["growth_pct"]]
        .reset_index()
        .rename(columns={"Continent": "continent"})
        .sort_values("growth_pct", ascending=False)
    )
    return _json(result)


@app.get("/consistent-decline")
def consistent_decline(lastXYears: int = Query(...), referenceYear: int = Query(...)):
    start = referenceYear - lastXYears - 1
    df = _fetch("/run", {"region": ALL_REGIONS, "startYear": start, "endYear": referenceYear})
    yearly = (
        df.groupby(["Country Name", "Year"])["Value"]
        .sum()
        .unstack("Year")
        .sort_index(axis=1)
    )

    def all_declining(row):
        vals = row.dropna().values
        return len(vals) == lastXYears and all(vals[i] > vals[i + 1] for i in range(len(vals) - 1))

    def avg_decline_pct(row):
        vals = row.dropna().values
        pct_changes = [(vals[i + 1] - vals[i]) / vals[i] * 100 for i in range(len(vals) - 1)]
        return sum(pct_changes) / len(pct_changes)

    mask = yearly.apply(all_declining, axis=1)
    result = yearly[mask].apply(avg_decline_pct, axis=1).reset_index()
    result.columns = ["country", "avg_decline_pct"]
    result = result.sort_values("avg_decline_pct")
    return _json(result)


@app.get("/continent-gdp-share")
def continent_gdp_share(startYear: int = Query(...), endYear: int = Query(...)):
    df = _fetch("/run", {"region": ALL_REGIONS, "startYear": startYear, "endYear": endYear})
    continent_total = df.groupby("Continent")["Value"].sum()
    global_total = continent_total.sum()
    result = (
        (continent_total / global_total * 100)
        .reset_index()
        .rename(columns={"Continent": "continent", "Value": "share_pct"})
        .sort_values("share_pct", ascending=False)
    )
    return _json(result)