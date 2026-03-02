"""
Diagnostic script — check /aggregate/country-code response shape.
Run with: python check_country_code.py
"""

import httpx
import json

CORE_URL = "http://localhost:8010"


def check():
    print("=" * 60)
    print(f"POST {CORE_URL}/aggregate/country-code")
    print("=" * 60)

    try:
        r = httpx.post(
            f"{CORE_URL}/aggregate/country-code",
            json={"region": "__ALL__"},
            timeout=30,
        )
        r.raise_for_status()
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return

    rows = r.json()

    print(f"\n✅ Status: {r.status_code}")
    print(f"📦 Total rows: {len(rows)}")

    if not rows:
        print("⚠️  Response is empty!")
        return

    print(f"\n🔑 Columns (keys in first row):")
    for key in rows[0].keys():
        print(f"   - {repr(key)}")

    print(f"\n📋 First 5 rows:")
    for row in rows[:5]:
        print(f"   {json.dumps(row, indent=None)}")

    print(f"\n📋 Last 2 rows:")
    for row in rows[-2:]:
        print(f"   {json.dumps(row, indent=None)}")


if __name__ == "__main__":
    check()
