from __future__ import annotations

import httpx
import time
from collections import defaultdict
from src.plugins.outputs import OutputSink, CoreAPIClient

BASE_URL = "http://localhost:8011"

# ── ANSI palette ──────────────────────────────────────────────────────────────
R = "\033[0m"
B = "\033[1m"
DIM = "\033[2m"

WHITE = "\033[97m"
GOLD = "\033[93m"
CYAN = "\033[96m"
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
MGNT = "\033[95m"
GRAY = "\033[90m"

BG_DARK = "\033[48;5;234m"
BG_MID = "\033[48;5;236m"

OK = f"{GREEN}●{R}"
ERR = f"{RED}✗{R}"

WIDTH = 72
SPARK = "▁▂▃▄▅▆▇█"


# ── Helpers ───────────────────────────────────────────────────────────────────


def _fmt_gdp(val: float) -> str:
    av = abs(val)
    if av >= 1e12:
        return f"{val/1e12:.2f}T"
    if av >= 1e9:
        return f"{val/1e9:.2f}B"
    if av >= 1e6:
        return f"{val/1e6:.2f}M"
    return f"{val:,.0f}"


def _bar(fraction: float, width: int = 20, color: str = CYAN) -> str:
    filled = max(0, min(width, round(fraction * width)))
    return f"{color}{'█' * filled}{GRAY}{'░' * (width - filled)}{R}"


def _sparkline(values: list[float]) -> str:
    if not values:
        return ""
    lo, hi = min(values), max(values)
    rng = hi - lo or 1
    return "".join(SPARK[int((v - lo) / rng * (len(SPARK) - 1))] for v in values)


def _rule(char: str = "─", color: str = GRAY) -> None:
    print(f"{color}{char * WIDTH}{R}")


def _section(title: str, subtitle: str = "") -> None:
    print()
    _rule()
    print(f"  {B}{GOLD}{title}{R}  {DIM}{GRAY}{subtitle}{R}")
    _rule()


def _status(name: str, code: int, rows: int | str, elapsed: float) -> None:
    icon = OK if code == 200 else ERR
    ccol = GREEN if code == 200 else RED
    rs = f"{rows} rows" if isinstance(rows, int) else rows
    print(
        f"\n  {icon}  {B}{WHITE}{name}{R}  {ccol}HTTP {code}{R}  {GRAY}{rs} · {elapsed*1000:.0f}ms{R}"
    )


def _fetch(base: str, path: str, params: dict):
    t0 = time.perf_counter()
    try:
        r = httpx.get(f"{base}{path}", params=params, timeout=30)
        return r.status_code, r.json(), time.perf_counter() - t0
    except Exception as e:
        return 0, None, time.perf_counter() - t0


# ── CliSink ───────────────────────────────────────────────────────────────────


class CliSink(OutputSink):

    def __init__(self, client: CoreAPIClient, analytics_url: str = BASE_URL):
        super().__init__(client)
        self._base = analytics_url.rstrip("/")

    def start(self) -> None:
        self._banner()
        self._top_countries()
        self._bottom_countries()
        self._gdp_growth_rate()
        self._avg_gdp_by_continent()
        self._global_gdp_trend()
        self._fastest_growing_continent()
        self._consistent_decline()
        self._continent_gdp_share()
        self._footer()

    # ── Banner ────────────────────────────────────────────────────────

    def _banner(self) -> None:
        print()
        print(f"  {GOLD}{'▄' * (WIDTH - 4)}{R}")
        print(f"  {BG_DARK}{GOLD}{B}{'  GDP ANALYTICS ENGINE':^{WIDTH - 4}}{R}")
        print(f"  {BG_DARK}{GRAY}{'  live · localhost:8011':^{WIDTH - 4}}{R}")
        print(f"  {GOLD}{'▀' * (WIDTH - 4)}{R}")

    # ── Sections ──────────────────────────────────────────────────────

    def _top_countries(self) -> None:
        params = {"continent": "Europe", "year": 2020, "n": 10}
        code, data, t = _fetch(self._base, "/top-countries", params)
        _section("Top 10 Countries by GDP", "Europe · 2020")
        _status("top-countries", code, len(data) if data else 0, t)
        if not data:
            return
        print()
        medals = ["🥇", "🥈", "🥉"]
        max_v = max(d["gdp"] for d in data)
        for i, d in enumerate(data):
            medal = medals[i] if i < 3 else f"  {GRAY}{i+1}.{R}"
            bar = _bar(d["gdp"] / max_v, 28, GOLD if i == 0 else CYAN)
            print(
                f"  {medal}  {WHITE}{d['country']:<30}{R} {bar}  {B}{WHITE}{_fmt_gdp(d['gdp'])}{R}"
            )

    def _bottom_countries(self) -> None:
        params = {"continent": "Europe", "year": 2020, "n": 10}
        code, data, t = _fetch(self._base, "/bottom-countries", params)
        _section("Bottom 10 Countries by GDP", "Europe · 2020")
        _status("bottom-countries", code, len(data) if data else 0, t)
        if not data:
            return
        print()
        max_v = max(d["gdp"] for d in data)
        for d in data:
            bar = _bar(d["gdp"] / max_v, 28, MGNT)
            print(
                f"  {GRAY}▪{R}  {WHITE}{d['country']:<30}{R} {bar}  {WHITE}{_fmt_gdp(d['gdp'])}{R}"
            )

    def _gdp_growth_rate(self) -> None:
        params = {"continent": "Europe", "startYear": 2015, "endYear": 2020}
        code, data, t = _fetch(self._base, "/gdp-growth-rate", params)
        _section("GDP Growth Rate by Country", "Europe · 2015 → 2020")
        _status("gdp-growth-rate", code, len(data) if data else 0, t)
        if not data:
            return

        buckets: dict[str, list[float]] = defaultdict(list)
        for row in data:
            buckets[row["country"]].append(row["growth_rate_pct"])

        summary = sorted(
            [
                {"country": c, "avg": sum(v) / len(v), "spark": _sparkline(v)}
                for c, v in buckets.items()
            ],
            key=lambda x: x["avg"],
            reverse=True,
        )

        print(f"\n  {B}{GOLD}{'Country':<30}{'Avg %':>8}  Trend{R}")
        print(f"  {GRAY}{'·' * 54}{R}")
        for row in summary[:15]:
            col = GREEN if row["avg"] >= 0 else RED
            sign = "+" if row["avg"] >= 0 else ""
            print(
                f"  {WHITE}{row['country']:<30}{R} {col}{sign}{row['avg']:>6.2f}%{R}  {CYAN}{row['spark']}{R}"
            )
        if len(summary) > 15:
            print(f"  {GRAY}  … {len(summary)-15} more countries{R}")

    def _avg_gdp_by_continent(self) -> None:
        params = {"startYear": 2015, "endYear": 2020}
        code, data, t = _fetch(self._base, "/avg-gdp-by-continent", params)
        _section("Average GDP by Continent", "2015 – 2020")
        _status("avg-gdp-by-continent", code, len(data) if data else 0, t)
        if not data:
            return
        print()
        data_s = sorted(data, key=lambda x: x["avg_gdp"], reverse=True)
        max_v = data_s[0]["avg_gdp"]
        for d in data_s:
            bar = _bar(d["avg_gdp"] / max_v, 28, BLUE)
            print(
                f"  {GOLD}{d['continent']:<26}{R} {bar}  {WHITE}{_fmt_gdp(d['avg_gdp'])}{R}"
            )

    def _global_gdp_trend(self) -> None:
        params = {"startYear": 2015, "endYear": 2020}
        code, data, t = _fetch(self._base, "/global-gdp-trend", params)
        _section("Total Global GDP Trend", "2015 – 2020")
        _status("global-gdp-trend", code, len(data) if data else 0, t)
        if not data:
            return
        data_s = sorted(data, key=lambda x: x["year"])
        vals = [d["total_gdp"] for d in data_s]
        max_v = max(vals)
        print(f"\n  {CYAN}{B}Sparkline  {_sparkline(vals)}{R}\n")
        for i, d in enumerate(data_s):
            delta = ""
            if i > 0:
                pct = (
                    (d["total_gdp"] - data_s[i - 1]["total_gdp"])
                    / data_s[i - 1]["total_gdp"]
                    * 100
                )
                col = GREEN if pct >= 0 else RED
                delta = f"  {col}{'▲' if pct >= 0 else '▼'} {abs(pct):.1f}%{R}"
            bar = _bar(d["total_gdp"] / max_v, 28, CYAN)
            print(
                f"  {GOLD}{d['year']}{R}  {bar}  {WHITE}{_fmt_gdp(d['total_gdp'])}{R}{delta}"
            )

    def _fastest_growing_continent(self) -> None:
        params = {"startYear": 2015, "endYear": 2020}
        code, data, t = _fetch(self._base, "/fastest-growing-continent", params)
        _section("Fastest Growing Continent", "2015 → 2020")
        _status("fastest-growing-continent", code, len(data) if data else 0, t)
        if not data:
            return
        data_s = sorted(data, key=lambda x: x["growth_pct"], reverse=True)
        max_abs = max(abs(d["growth_pct"]) for d in data_s) or 1
        medals = ["🥇", "🥈", "🥉"]
        print()
        for i, d in enumerate(data_s):
            pct = d["growth_pct"]
            col = GREEN if pct >= 0 else RED
            bar = _bar(abs(pct) / max_abs, 22, col)
            medal = medals[i] if i < 3 else f"  {GRAY}{i+1}.{R}"
            sign = "+" if pct >= 0 else ""
            print(
                f"  {medal}  {WHITE}{d['continent']:<22}{R} {bar}  {col}{B}{sign}{pct:.1f}%{R}"
            )

    def _consistent_decline(self) -> None:
        params = {"lastXYears": 3, "referenceYear": 2020}
        code, data, t = _fetch(self._base, "/consistent-decline", params)
        _section("Countries with Consistent GDP Decline", "last 3 yrs · ref 2020")
        _status("consistent-decline", code, len(data) if data else 0, t)
        if not data:
            print(f"\n  {GREEN}  No countries showed consistent decline.{R}")
            return
        data_s = sorted(data, key=lambda x: x["avg_decline_pct"])
        max_abs = max(abs(d["avg_decline_pct"]) for d in data_s) or 1
        print()
        for d in data_s:
            bar = _bar(abs(d["avg_decline_pct"]) / max_abs, 24, RED)
            print(
                f"  {RED}▼{R}  {WHITE}{d['country']:<28}{R} {bar}  {RED}{d['avg_decline_pct']:.2f}%/yr{R}"
            )

    def _continent_gdp_share(self) -> None:
        params = {"startYear": 2015, "endYear": 2020}
        code, data, t = _fetch(self._base, "/continent-gdp-share", params)
        _section("Continent Share of Global GDP", "2015 – 2020")
        _status("continent-gdp-share", code, len(data) if data else 0, t)
        if not data:
            return
        data_s = sorted(data, key=lambda x: x["share_pct"], reverse=True)
        colors = [GOLD, CYAN, GREEN, BLUE, MGNT, RED, WHITE]
        print()
        total = 0.0
        for i, d in enumerate(data_s):
            col = colors[i % len(colors)]
            bar = _bar(d["share_pct"] / 100, 30, col)
            print(
                f"  {col}{d['continent']:<24}{R} {bar}  {B}{WHITE}{d['share_pct']:.1f}%{R}"
            )
            total += d["share_pct"]
        print(f"\n  {GRAY}Total: {total:.1f}%{R}")

    # ── Footer ────────────────────────────────────────────────────────

    def _footer(self) -> None:
        print()
        print(f"  {GOLD}{'▄' * (WIDTH - 4)}{R}")
        print(f"  {BG_DARK}{GRAY}{'  all 8 tests complete':^{WIDTH - 4}}{R}")
        print(f"  {GOLD}{'▀' * (WIDTH - 4)}{R}")
        print()
