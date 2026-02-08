# test_palette.py
import pytest
from src.ui.palette import (
    CUSTOM_PALETTE,
    CONTINUOUS_PALETTES,
    DISCRETE_PALETTES,
    pick_color,
    pick_scale,
    LAYOUT
)


class TestPalette:
    def test_custom_palette_exists(self):
        assert CUSTOM_PALETTE is not None
        assert len(CUSTOM_PALETTE) == 4
    
    def test_custom_palette_colors(self):
        assert CUSTOM_PALETTE[0] == "#FF5555"
        assert CUSTOM_PALETTE[1] == "#FF937E"
        assert CUSTOM_PALETTE[2] == "#C1E59F"
        assert CUSTOM_PALETTE[3] == "#A3D78A"
    
    def test_continuous_palettes_structure(self):
        assert isinstance(CONTINUOUS_PALETTES, dict)
        assert "region" in CONTINUOUS_PALETTES
        assert "country_bar" in CONTINUOUS_PALETTES
        assert "country_treemap" in CONTINUOUS_PALETTES
        assert "year_scatter" in CONTINUOUS_PALETTES
        assert "year_bar" in CONTINUOUS_PALETTES
        assert "growth_rate" in CONTINUOUS_PALETTES
    
    def test_continuous_palettes_values(self):
        for key, value in CONTINUOUS_PALETTES.items():
            assert value == CUSTOM_PALETTE
    
    def test_discrete_palettes_structure(self):
        assert isinstance(DISCRETE_PALETTES, dict)
        assert "line" in DISCRETE_PALETTES
        assert "marker" in DISCRETE_PALETTES
        assert "highlight" in DISCRETE_PALETTES
        assert "background" in DISCRETE_PALETTES
    
    def test_discrete_palettes_line_marker_highlight(self):
        assert DISCRETE_PALETTES["line"] == CUSTOM_PALETTE
        assert DISCRETE_PALETTES["marker"] == CUSTOM_PALETTE
        assert DISCRETE_PALETTES["highlight"] == CUSTOM_PALETTE
    
    def test_discrete_palettes_background(self):
        assert DISCRETE_PALETTES["background"] == ["#111111", "#222222", "#333333"]


class TestPickColor:
    def test_pick_color_first_index(self):
        color = pick_color("line", 0)
        assert color == "#FF5555"
    
    def test_pick_color_second_index(self):
        color = pick_color("marker", 1)
        assert color == "#FF937E"
    
    def test_pick_color_cycles(self):
        color = pick_color("line", 4)
        assert color == "#FF5555"
    
    def test_pick_color_large_index(self):
        color = pick_color("marker", 10)
        assert color in CUSTOM_PALETTE
    
    def test_pick_color_unknown_palette(self):
        color = pick_color("unknown", 0)
        assert color == "#888888"
    
    def test_pick_color_background_palette(self):
        color = pick_color("background", 0)
        assert color == "#111111"
    
    def test_pick_color_default_index(self):
        color = pick_color("line")
        assert color == "#FF5555"


class TestPickScale:
    def test_pick_scale_region(self):
        scale = pick_scale("region")
        assert scale == CUSTOM_PALETTE
    
    def test_pick_scale_country_bar(self):
        scale = pick_scale("country_bar")
        assert scale == CUSTOM_PALETTE
    
    def test_pick_scale_year_scatter(self):
        scale = pick_scale("year_scatter")
        assert scale == CUSTOM_PALETTE
    
    def test_pick_scale_unknown(self):
        scale = pick_scale("unknown")
        assert scale == ["#888888"]
    
    def test_pick_scale_returns_list(self):
        scale = pick_scale("region")
        assert isinstance(scale, list)
        assert len(scale) == 4


class TestLayout:
    def test_layout_exists(self):
        assert LAYOUT is not None
        assert isinstance(LAYOUT, dict)
    
    def test_layout_template(self):
        assert LAYOUT["template"] == "plotly_dark"
    
    def test_layout_height(self):
        assert LAYOUT["height"] == 480
    
    def test_layout_title_position(self):
        assert LAYOUT["title_x"] == 0.5
    
    def test_layout_margins(self):
        assert "margin" in LAYOUT
        assert LAYOUT["margin"]["l"] == 40
        assert LAYOUT["margin"]["r"] == 40
        assert LAYOUT["margin"]["t"] == 60
        assert LAYOUT["margin"]["b"] == 40