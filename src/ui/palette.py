"""
Centralized color palette for all charts
Safe for Plotly large data and reruns
"""

from itertools import cycle

# Base custom colors
CUSTOM_PALETTE = ["#FF5555", "#FF937E", "#C1E59F", "#A3D78A"]

# Continuous palettes (used for color_continuous_scale)
CONTINUOUS_PALETTES = {
    "region_bar": CUSTOM_PALETTE,
    "country_treemap": CUSTOM_PALETTE,
    "year_scatter": CUSTOM_PALETTE,
    "year_bar": CUSTOM_PALETTE,
    "growth_rate": CUSTOM_PALETTE,
}

# Discrete / categorical palettes (used for lines, markers, single-color bars)
DISCRETE_PALETTES = {
    "line": CUSTOM_PALETTE,
    "marker": CUSTOM_PALETTE,
    "highlight": CUSTOM_PALETTE,
}

# Pick a discrete color (cycles safely)
def pick_color(palette_name: str, index: int = 0) -> str:
    colors = DISCRETE_PALETTES.get(palette_name, ["#888888"])
    return list(cycle(colors))[index]

# Pick a continuous scale (returns a copy to prevent mutation issues)
def pick_scale(scale_name: str) -> list[str]:
    return CONTINUOUS_PALETTES.get(scale_name, ["#888888"]).copy()

# Default layout for all charts
LAYOUT = dict(
    template="plotly_dark",
    height=480,
    title_x=0.5,
    margin=dict(l=40, r=40, t=60, b=40),
)
