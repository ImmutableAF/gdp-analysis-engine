from pathlib import Path
import streamlit as st

_BASE_DIR = Path(__file__).parent


def load_css(filename: str) -> None:
    css_path = _BASE_DIR / filename

    if not css_path.exists():
        raise FileNotFoundError(f"CSS file not found: {css_path.resolve()}")

    css = css_path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
