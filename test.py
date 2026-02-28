import httpx

API_BASE = "http://localhost:8010"


def main():
    print("=== Static config (GET /config) ===")
    r = httpx.get(f"{API_BASE}/config")
    r.raise_for_status()
    for k, v in r.json().items():
        print(f"  {k}: {v}")

    print("\n=== Reloaded config (POST /config/reload) ===")
    r = httpx.post(f"{API_BASE}/config/reload")
    r.raise_for_status()
    for k, v in r.json().items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()