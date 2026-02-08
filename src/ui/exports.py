"""
Export utilities
Responsible ONLY for data + chart exporting
Robust against Streamlit reruns & Kaleido issues
"""

import io
import zipfile
import streamlit as st


# ---------- CSV EXPORT ----------

def export_filtered_csv(df, filename="filtered_data.csv"):
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
    Two-phase, Kaleido-safe chart export:
    1) Generate images
    2) Download ZIP
    """

    figures = st.session_state.get("figures", [])

    # initialize state
    st.session_state.setdefault("charts_zip", None)
    st.session_state.setdefault("charts_ready", False)

    charts_available = len(figures) > 0

    # ⬇️ Create internal columns to keep these buttons side-by-side
    btn_col1, btn_col2 = st.columns(2)

    # --- Phase 1: Generate ---
    with btn_col1:
        generate_clicked = st.button(
            "Generate Charts (PNG)",
            disabled=not charts_available,
            help=None if charts_available else "No charts available to export",
            use_container_width=True,  # Optional: makes buttons fill their column
        )

    if generate_clicked:
        # Spinner can live outside columns or inside; 
        # putting it here keeps it centered or full width relative to the container
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
            use_container_width=True, # Optional: makes buttons fill their column
        )