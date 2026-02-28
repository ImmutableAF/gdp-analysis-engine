import httpx
import json

CORE_URL = "http://localhost:8010"

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def hit(method, path, body=None, params=None):
    url = f"{CORE_URL}{path}"
    try:
        if method == "GET":
            r = httpx.get(url, params=params, timeout=30)
        else:
            r = httpx.post(url, json=body or {}, timeout=30)

        print(f"\n[{r.status_code}] {method} {path}")
        data = r.json()

        if isinstance(data, list):
            print(f"  rows    : {len(data)}")
            print(f"  columns : {list(data[0].keys()) if data else '[]'}")
            print(f"  sample  : {json.dumps(data[0], indent=4)}" if data else "  (empty)")
        elif isinstance(data, dict):
            print(f"  keys    : {list(data.keys())}")
            print(f"  data    : {json.dumps(data, indent=4)}")
        else:
            print(f"  data    : {data}")

    except Exception as e:
        print(f"\n✗ {method} {path} — ERROR: {e}")


FILTERS = {"startYear": 2015, "endYear": 2020}
FILTERS_REGION = {**FILTERS, "region": "Asia"}

section("METADATA & CONFIG")
hit("GET", "/metadata")
hit("GET", "/config")

section("RAW DATA")
hit("GET", "/original")

section("PIPELINE /run")
hit("POST", "/run", body={})
hit("POST", "/run", body=FILTERS)
hit("POST", "/run", body=FILTERS_REGION)

section("AGGREGATIONS")
hit("POST", "/aggregate/region",       body=FILTERS)
hit("POST", "/aggregate/country",      body=FILTERS)
hit("POST", "/aggregate/country-code", body=FILTERS)
hit("POST", "/aggregate/all",          body=FILTERS)

section("AGGREGATIONS WITH operation=sum")
hit("POST", "/aggregate/region",  body={**FILTERS, "operation": "sum"})
hit("POST", "/aggregate/all",     body={**FILTERS, "operation": "sum"})