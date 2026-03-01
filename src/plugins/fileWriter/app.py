"""
FileOutputSink — dumps all GDP analytics results to a file.

Supported formats
─────────────────
  json      pretty-printed JSON, one object per section
  csv       one CSV file per section, zipped together
  markdown  single .md report with tables and sections
  html      standalone styled HTML report (dark theme)
  pdf       multi-page PDF report via reportlab
"""

from __future__ import annotations

import csv
import io
import json
import time
import zipfile
from ..outputs import CoreAPIClient, OutputSink
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

import httpx
from .format_picker import pick_format

# ── Format enum ───────────────────────────────────────────────────────────────


class FileFormat(StrEnum):
    JSON = "json"
    CSV = "csv"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"


# ── Shared fetch helper ───────────────────────────────────────────────────────


def _fetch(base: str, path: str, params: dict) -> tuple[int, Any, float]:
    t0 = time.perf_counter()
    try:
        r = httpx.get(f"{base}{path}", params=params, timeout=30)
        return r.status_code, r.json(), time.perf_counter() - t0
    except Exception as exc:
        return 0, None, time.perf_counter() - t0


def _fmt_gdp(val: float) -> str:
    av = abs(val)
    if av >= 1e12:
        return f"{val/1e12:.2f}T"
    if av >= 1e9:
        return f"{val/1e9:.2f}B"
    if av >= 1e6:
        return f"{val/1e6:.2f}M"
    return f"{val:,.0f}"


# ── Section definitions ───────────────────────────────────────────────────────

SECTIONS = [
    {
        "id": "top_countries",
        "title": "Top 10 Countries by GDP",
        "path": "/top-countries",
        "params": {"continent": "Europe", "year": 2020, "n": 10},
        "note": "Europe · 2020",
    },
    {
        "id": "bottom_countries",
        "title": "Bottom 10 Countries by GDP",
        "path": "/bottom-countries",
        "params": {"continent": "Europe", "year": 2020, "n": 10},
        "note": "Europe · 2020",
    },
    {
        "id": "gdp_growth_rate",
        "title": "GDP Growth Rate by Country",
        "path": "/gdp-growth-rate",
        "params": {"continent": "Europe", "startYear": 2015, "endYear": 2020},
        "note": "Europe · 2015 → 2020",
    },
    {
        "id": "avg_gdp_by_continent",
        "title": "Average GDP by Continent",
        "path": "/avg-gdp-by-continent",
        "params": {"startYear": 2015, "endYear": 2020},
        "note": "2015 – 2020",
    },
    {
        "id": "global_gdp_trend",
        "title": "Total Global GDP Trend",
        "path": "/global-gdp-trend",
        "params": {"startYear": 2015, "endYear": 2020},
        "note": "2015 – 2020",
    },
    {
        "id": "fastest_growing_continent",
        "title": "Fastest Growing Continent",
        "path": "/fastest-growing-continent",
        "params": {"startYear": 2015, "endYear": 2020},
        "note": "2015 → 2020",
    },
    {
        "id": "consistent_decline",
        "title": "Countries with Consistent GDP Decline",
        "path": "/consistent-decline",
        "params": {"lastXYears": 3, "referenceYear": 2020},
        "note": "last 3 yrs · ref 2020",
    },
    {
        "id": "continent_gdp_share",
        "title": "Continent Share of Global GDP",
        "path": "/continent-gdp-share",
        "params": {"startYear": 2015, "endYear": 2020},
        "note": "2015 – 2020",
    },
]


# ── FileOutputSink ────────────────────────────────────────────────────────────


class FileOutputSink(OutputSink):
    """
    Writes all analytics results to a file.

    Parameters
    ----------
    client        : CoreAPIClient (passed through to base class)
    fmt           : FileFormat  (json | csv | markdown | html | pdf)
    output_path   : where to write; defaults to ./gdp_report.<ext>
    analytics_url : base URL of the analytics API
    """

    DEFAULT_URL = "http://localhost:8011"

    def __init__(
        self,
        client: CoreAPIClient,
        fmt: FileFormat | str = FileFormat.HTML,
        output_path: Path | str | None = None,
        analytics_url: str = DEFAULT_URL,
    ):
        super().__init__(client)
        self._fmt = FileFormat(fmt)
        self._base = analytics_url.rstrip("/")
        self._path = (
            Path(output_path) if output_path else Path(f"gdp_report.{self._fmt}")
        )

    # ── Entry point ───────────────────────────────────────────────────

    def start(self) -> None:
        # Let the user pick the format interactively at runtime
        chosen = pick_format()
        self._fmt = FileFormat(chosen)
        self._path = self._path.with_suffix(
            ".zip" if self._fmt == FileFormat.CSV else f".{self._fmt}"
        )

        print(f"  Collecting data from {self._base} …")
        results = self._collect_all()

        print(f"  Writing {self._fmt.upper()} → {self._path}")
        match self._fmt:
            case FileFormat.JSON:
                self._write_json(results)
            case FileFormat.CSV:
                self._write_csv(results)
            case FileFormat.MARKDOWN:
                self._write_markdown(results)
            case FileFormat.HTML:
                self._write_html(results)
            case FileFormat.PDF:
                self._write_pdf(results)

        size = self._path.stat().st_size
        print(f"  Done — {self._path}  ({size/1024:.1f} KB)")

    # ── Data collection ───────────────────────────────────────────────

    def _collect_all(self) -> list[dict]:
        out = []
        for sec in SECTIONS:
            code, data, elapsed = _fetch(self._base, sec["path"], sec["params"])
            out.append(
                {
                    "id": sec["id"],
                    "title": sec["title"],
                    "note": sec["note"],
                    "params": sec["params"],
                    "status": code,
                    "elapsed": round(elapsed * 1000, 1),
                    "data": (
                        data if isinstance(data, list) else ([data] if data else [])
                    ),
                    "ok": code == 200 and data is not None,
                }
            )
            status = "✓" if code == 200 else "✗"
            rows = len(data) if isinstance(data, list) else ("1" if data else "0")
            print(
                f"    {status} {sec['title']:<44} {rows:>4} rows  {elapsed*1000:.0f}ms"
            )
        return out

    # ══════════════════════════════════════════════════════════════════
    # FORMAT WRITERS
    # ══════════════════════════════════════════════════════════════════

    # ── JSON ──────────────────────────────────────────────────────────

    def _write_json(self, results: list[dict]) -> None:
        payload = {
            "report": "GDP Analytics Engine",
            "generated_at": datetime.now().isoformat(),
            "sections": [
                {
                    "id": r["id"],
                    "title": r["title"],
                    "note": r["note"],
                    "params": r["params"],
                    "status": r["status"],
                    "elapsed_ms": r["elapsed"],
                    "rows": len(r["data"]),
                    "data": r["data"],
                }
                for r in results
            ],
        }
        self._path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # ── CSV (zip of CSVs) ─────────────────────────────────────────────

    def _write_csv(self, results: list[dict]) -> None:
        # Ensure .zip extension for multi-file output
        if self._path.suffix != ".zip":
            self._path = self._path.with_suffix(".zip")

        with zipfile.ZipFile(self._path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Index file
            idx = io.StringIO()
            w = csv.writer(idx)
            w.writerow(
                ["section", "title", "note", "http_status", "elapsed_ms", "rows"]
            )
            for r in results:
                w.writerow(
                    [
                        r["id"],
                        r["title"],
                        r["note"],
                        r["status"],
                        r["elapsed"],
                        len(r["data"]),
                    ]
                )
            zf.writestr("_index.csv", idx.getvalue())

            # One CSV per section
            for r in results:
                if not r["data"]:
                    continue
                buf = io.StringIO()
                keys = list(r["data"][0].keys())
                w2 = csv.DictWriter(buf, fieldnames=keys)
                w2.writeheader()
                w2.writerows(r["data"])
                zf.writestr(f"{r['id']}.csv", buf.getvalue())

    # ── Markdown ──────────────────────────────────────────────────────

    def _write_markdown(self, results: list[dict]) -> None:
        lines: list[str] = []
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")

        lines += [
            "# GDP Analytics Engine",
            f"",
            f"> Generated: {ts} &nbsp;|&nbsp; Source: `{self._base}`",
            "",
            "---",
            "",
            "## Table of Contents",
            "",
        ]
        for i, r in enumerate(results, 1):
            anchor = r["id"].replace("_", "-")
            lines.append(f"{i}. [{r['title']}](#{anchor})")
        lines += ["", "---", ""]

        for r in results:
            lines += [
                f"## {r['title']}",
                f"",
                f"**{r['note']}** &nbsp;·&nbsp; "
                f"HTTP `{r['status']}` &nbsp;·&nbsp; "
                f"{len(r['data'])} rows &nbsp;·&nbsp; "
                f"`{r['elapsed']} ms`",
                "",
            ]
            if not r["ok"] or not r["data"]:
                lines += ["> ⚠️ No data returned.", ""]
                continue

            keys = list(r["data"][0].keys())
            # Header
            lines.append(
                "| " + " | ".join(k.replace("_", " ").title() for k in keys) + " |"
            )
            lines.append("| " + " | ".join("---" for _ in keys) + " |")
            for row in r["data"]:
                cells = []
                for k in keys:
                    v = row[k]
                    if isinstance(v, float):
                        if (
                            "pct" in k
                            or "rate" in k
                            or "growth" in k
                            or "share" in k
                            or "decline" in k
                        ):
                            cells.append(f"{v:.2f}%")
                        elif "gdp" in k or "avg" in k or "total" in k:
                            cells.append(_fmt_gdp(v))
                        else:
                            cells.append(f"{v:.3f}")
                    else:
                        cells.append(str(v))
                lines.append("| " + " | ".join(cells) + " |")
            lines += ["", "---", ""]

        self._path.write_text("\n".join(lines), encoding="utf-8")

    # ── HTML ──────────────────────────────────────────────────────────

    def _write_html(self, results: list[dict]) -> None:
        ts = datetime.now().strftime("%B %d, %Y · %H:%M")

        def _fmt_cell(k: str, v: Any) -> str:
            if isinstance(v, float):
                if any(x in k for x in ("pct", "rate", "growth", "share", "decline")):
                    cls = "pos" if v >= 0 else "neg"
                    sign = "+" if v >= 0 else ""
                    return f'<span class="{cls}">{sign}{v:.2f}%</span>'
                elif any(x in k for x in ("gdp", "avg", "total")):
                    return f'<span class="money">{_fmt_gdp(v)}</span>'
                return f"{v:.3f}"
            return str(v)

        section_html = ""
        for i, r in enumerate(results, 1):
            status_cls = "ok" if r["ok"] else "err"
            status_dot = "●" if r["ok"] else "✗"
            rows_html = ""

            if r["ok"] and r["data"]:
                keys = list(r["data"][0].keys())
                thead = "".join(f"<th>{k.replace('_',' ').title()}</th>" for k in keys)
                tbody = ""
                for row in r["data"]:
                    cells = "".join(f"<td>{_fmt_cell(k, row[k])}</td>" for k in keys)
                    tbody += f"<tr>{cells}</tr>"
                rows_html = f"<table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table>"
            else:
                rows_html = '<p class="no-data">No data returned.</p>'

            section_html += f"""
        <section id="{r['id']}">
          <div class="sec-header">
            <span class="sec-num">{i:02d}</span>
            <div class="sec-meta">
              <h2>{r['title']}</h2>
              <span class="sec-note">{r['note']}</span>
            </div>
            <div class="sec-stats">
              <span class="{status_cls}">{status_dot} {r['status']}</span>
              <span class="dim">{len(r['data'])} rows</span>
              <span class="dim">{r['elapsed']} ms</span>
            </div>
          </div>
          {rows_html}
        </section>"""

        toc = "".join(
            f'<li><a href="#{r["id"]}">{r["title"]}</a></li>' for r in results
        )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GDP Analytics Engine</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

  :root {{
    --bg:      #0d0f12;
    --surface: #14171c;
    --border:  #1e2329;
    --border2: #2a3040;
    --gold:    #e8a623;
    --cyan:    #38bdf8;
    --green:   #4ade80;
    --red:     #f87171;
    --text:    #e2e8f0;
    --dim:     #64748b;
    --mono:    'IBM Plex Mono', monospace;
    --sans:    'IBM Plex Sans', sans-serif;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    font-size: 14px;
    line-height: 1.6;
  }}

  /* ── Header ── */
  header {{
    background: var(--surface);
    border-bottom: 1px solid var(--border2);
    padding: 2.5rem 3rem;
    display: flex;
    align-items: flex-end;
    gap: 2rem;
  }}
  header .title-block h1 {{
    font-family: var(--mono);
    font-size: 1.6rem;
    font-weight: 600;
    color: var(--gold);
    letter-spacing: 0.04em;
  }}
  header .title-block p {{
    color: var(--dim);
    font-size: 0.8rem;
    margin-top: 0.3rem;
    font-family: var(--mono);
  }}
  header .badges {{
    display: flex;
    gap: 0.5rem;
    margin-left: auto;
    align-items: center;
  }}
  .badge {{
    font-family: var(--mono);
    font-size: 0.72rem;
    padding: 0.25rem 0.75rem;
    border-radius: 2px;
    border: 1px solid var(--border2);
    color: var(--dim);
  }}
  .badge.gold {{ border-color: var(--gold); color: var(--gold); }}

  /* ── Layout ── */
  .layout {{ display: flex; min-height: calc(100vh - 90px); }}

  /* ── TOC sidebar ── */
  nav {{
    width: 260px;
    flex-shrink: 0;
    background: var(--surface);
    border-right: 1px solid var(--border);
    padding: 2rem 1.5rem;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
  }}
  nav h3 {{
    font-family: var(--mono);
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    color: var(--dim);
    text-transform: uppercase;
    margin-bottom: 1rem;
  }}
  nav ol {{ list-style: none; counter-reset: toc; }}
  nav ol li {{ counter-increment: toc; margin-bottom: 0.25rem; }}
  nav ol li::before {{
    content: counter(toc, decimal-leading-zero) ". ";
    font-family: var(--mono);
    color: var(--dim);
    font-size: 0.7rem;
  }}
  nav a {{
    color: var(--text);
    text-decoration: none;
    font-size: 0.8rem;
    opacity: 0.7;
    transition: opacity .15s;
  }}
  nav a:hover {{ opacity: 1; color: var(--cyan); }}

  /* ── Main content ── */
  main {{ flex: 1; padding: 2rem 3rem; max-width: 1100px; }}

  section {{
    margin-bottom: 3rem;
    border: 1px solid var(--border);
    border-radius: 4px;
    overflow: hidden;
  }}
  section:hover {{ border-color: var(--border2); }}

  .sec-header {{
    display: flex;
    align-items: center;
    gap: 1.25rem;
    padding: 1rem 1.5rem;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
  }}
  .sec-num {{
    font-family: var(--mono);
    font-size: 1.4rem;
    font-weight: 600;
    color: var(--gold);
    opacity: 0.4;
    min-width: 2.5rem;
  }}
  .sec-meta h2 {{
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text);
    letter-spacing: 0.01em;
  }}
  .sec-note {{
    font-family: var(--mono);
    font-size: 0.72rem;
    color: var(--dim);
  }}
  .sec-stats {{
    margin-left: auto;
    display: flex;
    gap: 1rem;
    font-family: var(--mono);
    font-size: 0.75rem;
    align-items: center;
  }}
  .sec-stats .dim {{ color: var(--dim); }}
  .sec-stats .ok  {{ color: var(--green); }}
  .sec-stats .err {{ color: var(--red); }}

  /* ── Table ── */
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
  }}
  thead tr {{
    background: #0f1318;
  }}
  th {{
    font-family: var(--mono);
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--dim);
    padding: 0.75rem 1.5rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }}
  td {{
    padding: 0.6rem 1.5rem;
    border-bottom: 1px solid var(--border);
    color: var(--text);
    font-variant-numeric: tabular-nums;
  }}
  tbody tr:last-child td {{ border-bottom: none; }}
  tbody tr:nth-child(even) {{ background: #0f1318; }}
  tbody tr:hover {{ background: #1a1f28; }}

  .money {{ font-family: var(--mono); color: var(--cyan); }}
  .pos   {{ color: var(--green); font-family: var(--mono); }}
  .neg   {{ color: var(--red);   font-family: var(--mono); }}

  .no-data {{
    padding: 1.5rem;
    color: var(--dim);
    font-style: italic;
    font-size: 0.85rem;
  }}

  /* ── Footer ── */
  footer {{
    text-align: center;
    padding: 2rem;
    color: var(--dim);
    font-family: var(--mono);
    font-size: 0.72rem;
    border-top: 1px solid var(--border);
    margin-top: 2rem;
  }}
</style>
</head>
<body>

<header>
  <div class="title-block">
    <h1>GDP ANALYTICS ENGINE</h1>
    <p>Generated {ts} · {self._base}</p>
  </div>
  <div class="badges">
    <span class="badge gold">8 SECTIONS</span>
    <span class="badge">{len([r for r in results if r['ok']])} PASSED</span>
    <span class="badge">{len([r for r in results if not r['ok']])} FAILED</span>
  </div>
</header>

<div class="layout">
  <nav>
    <h3>Contents</h3>
    <ol>{toc}</ol>
  </nav>
  <main>
    {section_html}
    <footer>GDP Analytics Engine · {ts}</footer>
  </main>
</div>

</body>
</html>"""

        self._path.write_text(html, encoding="utf-8")

    # ── PDF ───────────────────────────────────────────────────────────

    def _write_pdf(self, results: list[dict]) -> None:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            HRFlowable,
            PageBreak,
        )

        W, H = A4

        # Colour palette
        C_BG = colors.HexColor("#0d0f12")
        C_GOLD = colors.HexColor("#e8a623")
        C_CYAN = colors.HexColor("#38bdf8")
        C_GREEN = colors.HexColor("#4ade80")
        C_RED = colors.HexColor("#f87171")
        C_TEXT = colors.HexColor("#e2e8f0")
        C_DIM = colors.HexColor("#64748b")
        C_SURF = colors.HexColor("#14171c")
        C_BORDER = colors.HexColor("#1e2329")

        # Custom styles
        def S(name, **kw):
            return ParagraphStyle(name, **kw)

        sTitle = S(
            "sTitle",
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=C_GOLD,
            spaceAfter=4,
        )
        sSub = S(
            "sSub", fontName="Helvetica", fontSize=9, textColor=C_DIM, spaceAfter=2
        )
        sH2 = S(
            "sH2",
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=C_GOLD,
            spaceBefore=6,
            spaceAfter=2,
        )
        sNote = S(
            "sNote", fontName="Helvetica", fontSize=8, textColor=C_DIM, spaceAfter=6
        )
        sNoData = S(
            "sNoData", fontName="Helvetica-Oblique", fontSize=9, textColor=C_DIM
        )

        def _header_footer(canvas, doc):
            canvas.saveState()
            canvas.setFillColor(C_GOLD)
            canvas.setFont("Helvetica-Bold", 7)
            canvas.drawString(2 * cm, H - 1.2 * cm, "GDP ANALYTICS ENGINE")
            canvas.setFillColor(C_DIM)
            canvas.setFont("Helvetica", 7)
            canvas.drawRightString(
                W - 2 * cm, H - 1.2 * cm, datetime.now().strftime("%Y-%m-%d %H:%M")
            )
            canvas.setFillColor(C_DIM)
            canvas.drawCentredString(W / 2, 1 * cm, f"Page {doc.page}")
            canvas.setStrokeColor(C_BORDER)
            canvas.setLineWidth(0.5)
            canvas.line(2 * cm, H - 1.5 * cm, W - 2 * cm, H - 1.5 * cm)
            canvas.line(2 * cm, 1.4 * cm, W - 2 * cm, 1.4 * cm)
            canvas.restoreState()

        doc = SimpleDocTemplate(
            str(self._path),
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2.2 * cm,
            bottomMargin=2 * cm,
        )
        story = []

        # ── Cover ────────────────────────────────────────────────────
        story += [
            Spacer(1, 3 * cm),
            Paragraph("GDP ANALYTICS ENGINE", sTitle),
            Paragraph(
                f"Report generated {datetime.now().strftime('%B %d, %Y at %H:%M')}",
                sSub,
            ),
            Paragraph(f"Source: {self._base}", sSub),
            Spacer(1, 0.5 * cm),
            HRFlowable(width="100%", thickness=1, color=C_GOLD),
            Spacer(1, 0.5 * cm),
        ]

        # Summary table
        summary_data = [["Section", "Status", "Rows", "ms"]]
        for r in results:
            status = "✓ OK" if r["ok"] else f"✗ {r['status']}"
            summary_data.append(
                [r["title"], status, str(len(r["data"])), str(r["elapsed"])]
            )

        summary_tbl = Table(
            summary_data, colWidths=[10 * cm, 2.2 * cm, 1.5 * cm, 1.8 * cm]
        )
        summary_tbl.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("TEXTCOLOR", (0, 0), (-1, 0), C_GOLD),
                    ("TEXTCOLOR", (0, 1), (-1, -1), C_TEXT),
                    ("BACKGROUND", (0, 0), (-1, 0), C_SURF),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_BG, C_SURF]),
                    ("GRID", (0, 0), (-1, -1), 0.25, C_BORDER),
                    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        for i, r in enumerate(results, 1):
            color = C_GREEN if r["ok"] else C_RED
            summary_tbl.setStyle(TableStyle([("TEXTCOLOR", (1, i), (1, i), color)]))

        story += [summary_tbl, PageBreak()]

        # ── Data sections ────────────────────────────────────────────
        for i, r in enumerate(results, 1):
            story += [
                Paragraph(f"{i:02d}.  {r['title']}", sH2),
                Paragraph(
                    r["note"]
                    + f"  ·  HTTP {r['status']}  ·  {len(r['data'])} rows  ·  {r['elapsed']} ms",
                    sNote,
                ),
                HRFlowable(width="100%", thickness=0.5, color=C_BORDER),
                Spacer(1, 0.2 * cm),
            ]

            if not r["ok"] or not r["data"]:
                story += [Paragraph("No data returned.", sNoData), Spacer(1, 0.5 * cm)]
                continue

            keys = list(r["data"][0].keys())
            header = [k.replace("_", " ").title() for k in keys]
            rows = [header]

            for rec in r["data"]:
                row = []
                for k in keys:
                    v = rec[k]
                    if isinstance(v, float):
                        if any(
                            x in k
                            for x in ("pct", "rate", "growth", "share", "decline")
                        ):
                            sign = "+" if v >= 0 else ""
                            row.append(f"{sign}{v:.2f}%")
                        elif any(x in k for x in ("gdp", "avg", "total")):
                            row.append(_fmt_gdp(v))
                        else:
                            row.append(f"{v:.3f}")
                    else:
                        row.append(str(v))
                rows.append(row)

            # Dynamic column widths
            n = len(keys)
            avail = W - 4 * cm
            col_w = [avail / n] * n

            tbl = Table(rows, colWidths=col_w, repeatRows=1)

            # Build alternating row colours
            row_bg_cmds = []
            for ri in range(1, len(rows)):
                bg = C_BG if ri % 2 == 1 else C_SURF
                row_bg_cmds.append(("BACKGROUND", (0, ri), (-1, ri), bg))

            # Colour numeric columns
            num_color_cmds = []
            for ri, rec in enumerate(r["data"], 1):
                for ci, k in enumerate(keys):
                    v = rec.get(k)
                    if isinstance(v, float):
                        if any(
                            x in k
                            for x in ("pct", "rate", "growth", "share", "decline")
                        ):
                            col = C_GREEN if v >= 0 else C_RED
                            num_color_cmds.append(
                                ("TEXTCOLOR", (ci, ri), (ci, ri), col)
                            )
                        elif any(x in k for x in ("gdp", "avg", "total")):
                            num_color_cmds.append(
                                ("TEXTCOLOR", (ci, ri), (ci, ri), C_CYAN)
                            )

            tbl.setStyle(
                TableStyle(
                    [
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                        ("TEXTCOLOR", (0, 0), (-1, 0), C_GOLD),
                        ("TEXTCOLOR", (0, 1), (-1, -1), C_TEXT),
                        ("BACKGROUND", (0, 0), (-1, 0), C_SURF),
                        ("GRID", (0, 0), (-1, -1), 0.25, C_BORDER),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                        *row_bg_cmds,
                        *num_color_cmds,
                    ]
                )
            )
            story += [tbl, Spacer(1, 0.8 * cm)]

        doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
