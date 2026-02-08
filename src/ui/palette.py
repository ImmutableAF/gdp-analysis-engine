"""
Centralized color palette for all charts.
"""

from itertools import cycle

CUSTOM_PALETTE = ["#FF5555", "#FF937E", "#C1E59F", "#A3D78A"]

# Continuous color scales (plain lists, compatible with px.bar/px.scatter)
CONTINUOUS_PALETTES = {
    "region": CUSTOM_PALETTE,
    "country_bar": CUSTOM_PALETTE,
    "country_treemap": CUSTOM_PALETTE,
    "year_scatter": CUSTOM_PALETTE,
    "year_bar": CUSTOM_PALETTE,
    "growth_rate": CUSTOM_PALETTE,
}

# Discrete / categorical colors
DISCRETE_PALETTES = {
    "line": CUSTOM_PALETTE,
    "marker": CUSTOM_PALETTE,
    "highlight": CUSTOM_PALETTE,
    "background": ["#111111", "#222222", "#333333"],
}

# Pick a discrete color
def pick_color(palette_name: str, index: int = 0) -> str:
    colors = DISCRETE_PALETTES.get(palette_name, ["#888888"])
    return list(cycle(colors))[index]

# Pick a continuous colorscale (just return the list)
def pick_scale(scale_name: str) -> list[str]:
    return CONTINUOUS_PALETTES.get(scale_name, ["#888888"])

# Default layout
LAYOUT = dict(
    template="plotly_dark",
    height=480,
    title_x=0.5,
    margin=dict(l=40, r=40, t=60, b=40),
)