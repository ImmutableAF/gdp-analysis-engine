import json
import requests

BASE = "http://localhost:8000"


def test_metadata():
    r = requests.get(f"{BASE}/metadata")
    print(f"[metadata] status={r.status_code}")
    if r.ok:
        print(f"[metadata] body={json.loads(r.text)}\n")
    else:
        print(f"[metadata] error={r.text[:500]}\n")


def test_config():
    r = requests.get(f"{BASE}/config")
    print(f"[config] status={r.status_code}")
    if r.ok:
        print(f"[config] body={json.loads(r.text)}\n")
    else:
        print(f"[config] error={r.text[:500]}\n")


def test_original():
    r = requests.get(f"{BASE}/original")
    print(f"[original] status={r.status_code}")
    if r.ok:
        data = json.loads(r.text)
        print(f"[original] rows={len(data)}")
        print(f"[original] first row={data[0]}\n")
    else:
        print(f"[original] error={r.text[:500]}\n")


def test_run():
    payload = {
        "filters": {
            "region": "Europe",
            "country": None,
            "startYear": 2000,
            "endYear": 2020,
            "operation": None,
        }
    }
    r = requests.post(f"{BASE}/run", json=payload)
    print(f"[run] status={r.status_code}")
    if r.ok:
        data = json.loads(r.text)
        print(f"[run] rows={len(data)}")
        print(f"[run] first row={data[0]}\n")
    else:
        print(f"[run] error={r.text}\n")


if __name__ == "__main__":
    test_metadata()
    test_config()
    test_original()
    test_run()
