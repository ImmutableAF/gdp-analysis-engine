import pytest
from pathlib import Path


@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    """After tests finish, append custom.css into coverage's generated stylesheet."""
    coverage_dir = Path(".dev/reports/tests_coverage")
    css_src = coverage_dir / "custom.css"

    if not coverage_dir.exists():
        print("\n[css] Coverage folder not found — skipping CSS injection.")
        return

    if not css_src.exists():
        print("\n[css] custom.css not found — skipping CSS injection.")
        return

    # Coverage generates a hashed filename like style_cb_5c747636.css — find it dynamically
    candidates = [
        f for f in coverage_dir.glob("style_cb*.css") if f.name != "custom.css"
    ]

    if not candidates:
        print("\n[css] No style_cb*.css found — coverage may not have run yet.")
        return

    css_dest = candidates[0]  # always exactly one
    custom = css_src.read_text(encoding="utf-8")
    existing = css_dest.read_text(encoding="utf-8")

    marker = "/* GDP Analysis Engine — Custom Coverage Report Theme */"
    if marker in existing:
        # Re-inject fresh copy on repeated runs
        pre = existing[: existing.index(marker)]
        css_dest.write_text(pre + custom, encoding="utf-8")
        print(f"\n[css] Re-injected custom CSS → {css_dest.name}")
    else:
        css_dest.write_text(existing + "\n\n" + custom, encoding="utf-8")
        print(f"\n[css] Appended custom CSS → {css_dest.name}")
