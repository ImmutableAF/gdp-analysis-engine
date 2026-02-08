# test_charts.py
import pytest
import pandas as pd
import plotly.graph_objects as go
from unittest.mock import patch
from src.ui.charts import (
    CUSTOM_PALETTE,
    _require_columns,
    _aggregate_by_year,
    _make_continuous,
    _safe_palette,
    region_bar,
    country_bar,
    country_treemap,
    year_scatter,
    year_line,
    year_bar,
    growth_rate
)


class TestRequireColumns:
    def test_passes_when_columns_exist(self):
        df = pd.DataFrame({'A': [1], 'B': [2], 'C': [3]})
        _require_columns(df, {'A', 'B'}, 'test_chart')
    
    def test_raises_when_column_missing(self):
        df = pd.DataFrame({'A': [1], 'B': [2]})
        with pytest.raises(ValueError, match="missing columns"):
            _require_columns(df, {'A', 'C'}, 'test_chart')
    
    def test_raises_with_chart_name(self):
        df = pd.DataFrame({'A': [1]})
        with pytest.raises(ValueError, match="my_chart"):
            _require_columns(df, {'B'}, 'my_chart')


class TestAggregateByYear:
    def test_aggregates_by_year(self):
        df = pd.DataFrame({
            'Year': [2000, 2000, 2001],
            'Value': [100, 200, 300]
        })
        result = _aggregate_by_year(df, interpolate=False)
        
        assert len(result) == 2
        assert result[result['Year'] == 2000]['Value'].iloc[0] == 300
        assert result[result['Year'] == 2001]['Value'].iloc[0] == 300
    
    def test_sorts_by_year(self):
        df = pd.DataFrame({
            'Year': [2002, 2000, 2001],
            'Value': [100, 200, 300]
        })
        result = _aggregate_by_year(df, interpolate=False)
        
        assert result['Year'].tolist() == [2000, 2001, 2002]
    
    def test_interpolates_when_enabled(self):
        df = pd.DataFrame({
            'Year': [2000, 2001, 2002],
            'Value': [100, None, 300]
        })
        result = _aggregate_by_year(df, interpolate=True)
        
        assert not result['Value'].isna().any()


class TestMakeContinuous:
    def test_returns_list(self):
        result = _make_continuous(['#FF0000', '#00FF00'], steps=10)
        assert isinstance(result, list)
    
    def test_single_color_repeats(self):
        result = _make_continuous(['#FF0000'], steps=5)
        assert len(result) == 5
    
    def test_fallback_without_matplotlib(self):
        with patch('ui.charts.LinearSegmentedColormap', side_effect=ImportError):
            result = _make_continuous(['#FF0000', '#00FF00'], steps=10)
            assert len(result) > 0


class TestSafePalette:
    def test_continuous_for_small_n(self):
        use_cont, palette = _safe_palette(10, 'test_chart', max_cont=30)
        assert use_cont is True
        assert isinstance(palette, list)
    
    def test_discrete_for_large_n(self):
        use_cont, palette = _safe_palette(50, 'test_chart', max_cont=30)
        assert use_cont is False
        assert len(palette) == 50
    
    def test_discrete_cycles_colors(self):
        use_cont, palette = _safe_palette(10, 'test_chart', max_cont=5)
        assert palette[0] == CUSTOM_PALETTE[0]
        assert palette[4] == CUSTOM_PALETTE[0]


class TestRegionBar:
    def test_returns_figure(self):
        df = pd.DataFrame({
            'Continent': ['Asia', 'Europe'],
            'Value': [100, 200]
        })
        fig = region_bar(df)
        assert isinstance(fig, go.Figure)
    
    def test_empty_dataframe_returns_empty_figure(self):
        df = pd.DataFrame()
        fig = region_bar(df)
        assert isinstance(fig, go.Figure)
    
    def test_raises_on_missing_columns(self):
        df = pd.DataFrame({'Continent': ['Asia']})
        with pytest.raises(ValueError):
            region_bar(df)
    
    def test_sorts_descending(self):
        df = pd.DataFrame({
            'Continent': ['Asia', 'Europe', 'Africa'],
            'Value': [100, 300, 200]
        })
        fig = region_bar(df)
        assert fig.data[0].x[0] == 'Europe'


class TestCountryBar:
    def test_returns_figure(self):
        df = pd.DataFrame({
            'Country Code': ['US', 'CN'],
            'Value': [100, 200]
        })
        fig = country_bar(df)
        assert isinstance(fig, go.Figure)
    
    def test_limits_to_top_n(self):
        df = pd.DataFrame({
            'Country Code': ['A', 'B', 'C', 'D', 'E'],
            'Value': [50, 40, 30, 20, 10]
        })
        fig = country_bar(df, top_n=3)
        assert len(fig.data[0].x) == 3
    
    def test_shows_all_when_top_n_none(self):
        df = pd.DataFrame({
            'Country Code': ['A', 'B', 'C'],
            'Value': [100, 200, 300]
        })
        fig = country_bar(df, top_n=None)
        assert len(fig.data[0].x) == 3
    
    def test_empty_returns_empty_figure(self):
        df = pd.DataFrame()
        fig = country_bar(df)
        assert isinstance(fig, go.Figure)


class TestCountryTreemap:
    def test_returns_figure(self):
        df = pd.DataFrame({
            'Country Code': ['US', 'CN'],
            'Value': [100, 200]
        })
        fig = country_treemap(df)
        assert isinstance(fig, go.Figure)
    
    def test_limits_to_top_n(self):
        df = pd.DataFrame({
            'Country Code': ['A', 'B', 'C', 'D'],
            'Value': [40, 30, 20, 10]
        })
        fig = country_treemap(df, top_n=2)
        assert len(fig.data[0].labels) == 2


class TestYearScatter:
    def test_returns_figure(self):
        df = pd.DataFrame({
            'Year': [2000, 2001],
            'Value': [100, 200]
        })
        fig = year_scatter(df)
        assert isinstance(fig, go.Figure)
    
    def test_interpolates_when_enabled(self):
        df = pd.DataFrame({
            'Year': [2000, 2001, 2002],
            'Value': [100, None, 200]
        })
        fig = year_scatter(df, interpolate=True)
        assert isinstance(fig, go.Figure)


class TestYearLine:
    def test_returns_figure(self):
        df = pd.DataFrame({
            'Year': [2000, 2001],
            'Value': [100, 200]
        })
        fig = year_line(df)
        assert isinstance(fig, go.Figure)
    
    def test_uses_custom_color(self):
        df = pd.DataFrame({
            'Year': [2000, 2001],
            'Value': [100, 200]
        })
        fig = year_line(df)
        assert fig.data[0].line.color == CUSTOM_PALETTE[0]


class TestYearBar:
    def test_returns_figure(self):
        df = pd.DataFrame({
            'Year': [2000, 2001],
            'Value': [100, 200]
        })
        fig = year_bar(df)
        assert isinstance(fig, go.Figure)


class TestGrowthRate:
    def test_returns_none_for_single_year(self):
        df = pd.DataFrame({
            'Year': [2000],
            'Value': [100]
        })
        fig = growth_rate(df)
        assert fig is None
    
    def test_calculates_growth_rate(self):
        df = pd.DataFrame({
            'Year': [2000, 2001, 2002],
            'Value': [100, 110, 121]
        })
        fig = growth_rate(df)
        assert isinstance(fig, go.Figure)
    
    def test_returns_none_when_empty_after_dropna(self):
        df = pd.DataFrame({
            'Year': [2000, 2001],
            'Value': [None, None]
        })
        fig = growth_rate(df)
        assert fig is None