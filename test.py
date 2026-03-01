import httpx
import json

BASE_URL = "http://localhost:8011"  # change to your analytics API URL

PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"


def test(name: str, method: str, path: str, params: dict):
    url = f"{BASE_URL}{path}"
    try:
        r = httpx.request(method, url, params=params, timeout=30)
        data = r.json()
        status = PASS if r.status_code == 200 else FAIL
        preview = json.dumps(data[:2] if isinstance(data, list) else data, indent=2)
        print(f"{status} [{r.status_code}] {name}")
        print(f"   params : {params}")
        print(f"   rows   : {len(data) if isinstance(data, list) else 'N/A'}")
        print(f"   preview: {preview[:300]}")
    except Exception as e:
        print(f"{FAIL} {name} — ERROR: {e}")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("  GDP Analytics API — Test Suite")
    print("=" * 60)
    print()

    test(
        name="1. Top 10 Countries by GDP",
        method="GET",
        path="/top-countries",
        params={"continent": "Europe", "year": 2020, "n": 10},
    )

    test(
        name="2. Bottom 10 Countries by GDP",
        method="GET",
        path="/bottom-countries",
        params={"continent": "Europe", "year": 2020, "n": 10},
    )

    test(
        name="3. GDP Growth Rate by Country",
        method="GET",
        path="/gdp-growth-rate",
        params={"continent": "Europe", "startYear": 2015, "endYear": 2020},
    )

    test(
        name="4. Average GDP by Continent",
        method="GET",
        path="/avg-gdp-by-continent",
        params={"startYear": 2015, "endYear": 2020},
    )

    test(
        name="5. Total Global GDP Trend",
        method="GET",
        path="/global-gdp-trend",
        params={"startYear": 2015, "endYear": 2020},
    )

    test(
        name="6. Fastest Growing Continent",
        method="GET",
        path="/fastest-growing-continent",
        params={"startYear": 2015, "endYear": 2020},
    )

    test(
        name="7. Countries with Consistent GDP Decline",
        method="GET",
        path="/consistent-decline",
        params={"lastXYears": 3, "referenceYear": 2020},
    )

    test(
        name="8. Continent Share of Global GDP",
        method="GET",
        path="/continent-gdp-share",
        params={"startYear": 2015, "endYear": 2020},
    )
