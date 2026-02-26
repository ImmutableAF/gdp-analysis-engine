"""
Export Utilities
================

CSV and PNG chart export functionality. Handles Streamlit reruns and Kaleido
rendering issues with two-phase export strategy.

Functions
---------
export_filtered_csv(df, filename)
    Download filtered data as CSV
export_charts_as_png()
    Two-phase PNG chart export (generate then download)

See Also
--------
views : UI rendering layer
charts : Chart generation functions

Notes
-----
Two-phase chart export prevents Kaleido Windows issues:
1. Generate: Render all charts to PNG and create ZIP
2. Download: Provide ZIP for download

State management via st.session_state ensures stability across reruns.

Examples
--------
In Streamlit app:
>>> export_filtered_csv(df, "my_data.csv")
>>> export_charts_as_png()
"""

import io
import zipfile
import streamlit as st


# ---------- CSV EXPORT ----------


def export_filtered_csv(df, filename="filtered_data.csv"):
    """
    Create download button for filtered DataFrame as CSV.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to export
    filename : str, default="filtered_data.csv"
        Download filename

    Notes
    -----
    Button disabled if DataFrame empty. Uses Streamlit download_button.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({"Country": ["USA"], "GDP": [20e12]})
    >>> export_filtered_csv(df, "gdp_export.csv")
    """
    ready = not df.empty

    st.download_button(
        "Download Filtered CSV",
        df.to_csv(index=False) if ready else "",
        file_name=filename,
        mime="text/csv",
        disabled=not ready,
        help=None if ready else "No data available for export",
    )


# ---------- CHART EXPORT ----------


def export_charts_as_png():
    """
    Two-phase PNG chart export with Kaleido error handling.

    Phase 1 (Generate): Renders all registered charts to PNG and creates ZIP.
    Phase 2 (Download): Provides ZIP download button.

    Requires st.session_state.figures list of (name, figure) tuples.

    Notes
    -----
    Uses session state to persist ZIP between reruns:
    - charts_zip: BytesIO ZIP buffer
    - charts_ready: Boolean flag for download readiness

    Handles Kaleido Windows limitations with user-friendly error messages.
    Layout uses two columns for Generate/Download buttons.

    Examples
    --------
    In Streamlit view:
    >>> # After registering figures
    >>> st.session_state.figures = [("chart1", fig1), ("chart2", fig2)]
    >>> export_charts_as_png()
    """
    figures = st.session_state.get("figures", [])

    # initialize state
    st.session_state.setdefault("charts_zip", None)
    st.session_state.setdefault("charts_ready", False)

    charts_available = len(figures) > 0

    # Create internal columns to keep buttons side-by-side
    btn_col1, btn_col2 = st.columns(2)

    # --- Phase 1: Generate ---
    with btn_col1:
        generate_clicked = st.button(
            "Generate Charts (PNG)",
            disabled=not charts_available,
            help=None if charts_available else "No charts available to export",
            use_container_width=True,
        )

    if generate_clicked:
        with st.spinner("Rendering charts… this may take a moment"):
            buffer = io.BytesIO()

            try:
                with zipfile.ZipFile(buffer, "w") as zipf:
                    for name, fig in figures:
                        img = fig.to_image(format="png", scale=2)
                        zipf.writestr(f"{name}.png", img)

                buffer.seek(0)
                st.session_state.charts_zip = buffer
                st.session_state.charts_ready = True

            except Exception as e:
                st.session_state.charts_zip = None
                st.session_state.charts_ready = False
                st.error(
                    "Chart export failed.\n\n"
                    "This is a known Kaleido + Windows limitation. "
                    "Try once per session or restart the app."
                )

    # --- Phase 2: Download ---
    with btn_col2:
        st.download_button(
            "Download Charts ZIP",
            data=st.session_state.charts_zip if st.session_state.charts_ready else b"",
            file_name="charts_png_export.zip",
            mime="application/zip",
            disabled=not st.session_state.charts_ready,
            help=None if st.session_state.charts_ready else "Generate charts first",
            use_container_width=True,
        )
