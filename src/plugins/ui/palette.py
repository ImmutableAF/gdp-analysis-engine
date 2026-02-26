"""
Centralized Color Palette
==========================

Color scheme constants for consistent chart styling across the application.

Constants
---------
CUSTOM_PALETTE : list[str]
    Primary 4-color palette
CONTINUOUS_PALETTES : dict
    Continuous scales for different chart types
DISCRETE_PALETTES : dict
    Discrete colors for specific elements
LAYOUT : dict
    Default Plotly layout configuration

Functions
---------
pick_color(palette_name, index)
    Select discrete color from palette
pick_scale(scale_name)
    Get continuous colorscale

See Also
--------
charts : Chart generation using these palettes

Examples
--------
>>> color = pick_color("line", 0)
>>> print(color)
#FF5555

>>> scale = pick_scale("region")
>>> print(scale)
['#FF5555', '#FF937E', '#C1E59F', '#A3D78A']
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


def pick_color(palette_name: str, index: int = 0) -> str:
    """
    Select discrete color from palette by index.

    Parameters
    ----------
    palette_name : str
        Palette name from DISCRETE_PALETTES
    index : int, default=0
        Color index (cycles if exceeds palette length)

    Returns
    -------
    str
        Hex color code, "#888888" if palette not found

    Examples
    --------
    >>> pick_color("line", 0)
    '#FF5555'
    >>> pick_color("marker", 5)  # Cycles through palette
    '#FF937E'
    """
    colors = DISCRETE_PALETTES.get(palette_name, ["#888888"])
    return list(cycle(colors))[index]


def pick_scale(scale_name: str) -> list[str]:
    """
    Get continuous colorscale by name.

    Parameters
    ----------
    scale_name : str
        Scale name from CONTINUOUS_PALETTES

    Returns
    -------
    list[str]
        Color list, ["#888888"] if scale not found

    Examples
    --------
    >>> pick_scale("region")
    ['#FF5555', '#FF937E', '#C1E59F', '#A3D78A']
    """
    return CONTINUOUS_PALETTES.get(scale_name, ["#888888"])


# Default layout
LAYOUT = dict(
    template="plotly_dark",
    height=480,
    title_x=0.5,
    margin=dict(l=40, r=40, t=60, b=40),
)
