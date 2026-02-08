# test_views.py
import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock, call
from src.ui.views import (
    _register_figure,
    _render_aggregate_metrics,
    _render_filtered_data_preview,
    render_region_analysis,
    render_year_analysis,
    render_country_analysis,
    render_exports
)


class TestRegisterFigure:
    @patch('ui.views.st')
    def test_appends_figure_to_session_state(self, mock_st):
        mock_st.session_state.figures = []
        mock_fig = Mock()
        
        _register_figure('test_chart', mock_fig)
        
        assert len(mock_st.session_state.figures) == 1
        assert mock_st.session_state.figures[0] == ('test_chart', mock_fig)
    
    @patch('ui.views.st')
    def test_appends_multiple_figures(self, mock_st):
        mock_st.session_state.figures = []
        
        _register_figure('chart1', Mock())
        _register_figure('chart2', Mock())
        
        assert len(mock_st.session_state.figures) == 2


class TestRenderAggregateMetrics:
    @patch('ui.views.st')
    def test_renders_metrics_card(self, mock_st):
        df = pd.DataFrame({'Value': [100, 200, 300]})
        
        _render_aggregate_metrics(df, 'Test Scope')
        
        mock_st.markdown.assert_called()
        call_args = str(mock_st.markdown.call_args_list)
        assert 'Test Scope' in call_args
    
    @patch('ui.views.st')
    def test_formats_large_values(self, mock_st):
        df = pd.DataFrame({'Value': [1e12, 2e12]})
        
        _render_aggregate_metrics(df, 'Test')
        
        call_args = str(mock_st.markdown.call_args_list)
        assert 'T' in call_args  # Trillions
    
    @patch('ui.views.st')
    def test_calculates_total_gdp(self, mock_st):
        df = pd.DataFrame({'Value': [100, 200, 300]})
        
        _render_aggregate_metrics(df, 'Test')
        
        call_args = str(mock_st.markdown.call_args_list)
        assert '600' in call_args or '$600' in call_args
    
    @patch('ui.views.st')
    def test_calculates_average_gdp(self, mock_st):
        df = pd.DataFrame({'Value': [100, 200, 300]})
        
        _render_aggregate_metrics(df, 'Test')
        
        call_args = str(mock_st.markdown.call_args_list)
        assert '200' in call_args or '$200' in call_args
    
    @patch('ui.views.st')
    def test_shows_data_entries_count(self, mock_st):
        df = pd.DataFrame({'Value': [100, 200, 300]})
        
        _render_aggregate_metrics(df, 'Test')
        
        call_args = str(mock_st.markdown.call_args_list)
        assert '3' in call_args


class TestRenderFilteredDataPreview:
    @patch('ui.views.st')
    def test_creates_expander(self, mock_st):
        df = pd.DataFrame({'Year': [2000], 'Country Code': ['US'], 'Value': [100]})
        
        _render_filtered_data_preview(df)
        
        mock_st.expander.assert_called_once()
    
    @patch('ui.views.st')
    def test_displays_dataframe(self, mock_st):
        df = pd.DataFrame({'Year': [2000], 'Country Code': ['US'], 'Value': [100]})
        mock_expander = MagicMock()
        mock_st.expander.return_value.__enter__ = Mock(return_value=mock_expander)
        mock_st.expander.return_value.__exit__ = Mock()
        
        _render_filtered_data_preview(df)
        
        mock_st.dataframe.assert_called_once()


class TestRenderRegionAnalysis:
    @patch('ui.views.st')
    @patch('ui.views.pipeline')
    @patch('ui.views.charts')
    def test_renders_for_all_regions(self, mock_charts, mock_pipeline, mock_st):
        df = pd.DataFrame({
            'Continent': ['Asia', 'Europe'],
            'Value': [100, 200]
        })
        mock_pipeline.apply_filters.return_value = df
        mock_pipeline.aggregate_by_region.return_value = df
        mock_charts.region_bar.return_value = Mock()
        mock_st.session_state.figures = []
        
        render_region_analysis(df, None, 2000, 2020, 'sum', 10)
        
        mock_charts.region_bar.assert_called_once()
    
    @patch('ui.views.st')
    @patch('ui.views.pipeline')
    @patch('ui.views.charts')
    def test_renders_for_specific_region(self, mock_charts, mock_pipeline, mock_st):
        df = pd.DataFrame({
            'Continent': ['Asia'],
            'Country Code': ['CN'],
            'Value': [100]
        })
        mock_pipeline.apply_filters.return_value = df
        mock_pipeline.aggregate_by_country_code.return_value = df
        mock_charts.country_bar.return_value = Mock()
        mock_charts.country_treemap.return_value = Mock()
        mock_st.session_state.figures = []
        
        render_region_analysis(df, 'Asia', 2000, 2020, 'sum', 10)
        
        mock_charts.country_bar.assert_called_once()
        mock_charts.country_treemap.assert_called_once()
    
    @patch('ui.views.st')
    @patch('ui.views.pipeline')
    def test_applies_filters(self, mock_pipeline, mock_st):
        df = pd.DataFrame({'Continent': ['Asia'], 'Value': [100]})
        mock_pipeline.apply_filters.return_value = df
        mock_pipeline.aggregate_by_region.return_value = df
        mock_st.session_state.figures = []
        
        render_region_analysis(df, 'Asia', 2000, 2020, 'sum', 10)
        
        mock_pipeline.apply_filters.assert_called_once_with(
            df,
            region='Asia',
            start_year=2000,
            end_year=2020
        )


class TestRenderYearAnalysis:
    @patch('ui.views.st')
    @patch('ui.views.pipeline')
    @patch('ui.views.charts')
    def test_shows_info_for_single_year(self, mock_charts, mock_pipeline, mock_st):
        df = pd.DataFrame({'Year': [2000], 'Value': [100]})
        df['Year'] = pd.Series([2000], dtype=int)
        mock_pipeline.apply_filters.return_value = df
        
        render_year_analysis(df, None, 2000, 2000)
        
        mock_st.info.assert_called_once()
    
    @patch('ui.views.st')
    @patch('ui.views.pipeline')
    @patch('ui.views.charts')
    def test_renders_charts_for_multiple_years(self, mock_charts, mock_pipeline, mock_st):
        df = pd.DataFrame({'Year': [2000, 2001], 'Value': [100, 200]})
        mock_pipeline.apply_filters.return_value = df
        mock_charts.year_scatter.return_value = Mock()
        mock_charts.growth_rate.return_value = Mock()
        mock_st.session_state.figures = []
        
        render_year_analysis(df, None, 2000, 2001)
        
        mock_charts.year_scatter.assert_called_once()
        mock_charts.growth_rate.assert_called_once()
    
    @patch('ui.views.st')
    @patch('ui.views.pipeline')
    @patch('ui.views.charts')
    def test_handles_none_growth_rate(self, mock_charts, mock_pipeline, mock_st):
        df = pd.DataFrame({'Year': [2000, 2001], 'Value': [100, 200]})
        mock_pipeline.apply_filters.return_value = df
        mock_charts.year_scatter.return_value = Mock()
        mock_charts.growth_rate.return_value = None
        mock_st.session_state.figures = []
        
        render_year_analysis(df, None, 2000, 2001)
        
        assert mock_st.plotly_chart.call_count == 1


class TestRenderCountryAnalysis:
    @patch('ui.views.st')
    @patch('ui.views.pipeline')
    @patch('ui.views.charts')
    def test_renders_country_charts(self, mock_charts, mock_pipeline, mock_st):
        df = pd.DataFrame({'Country Name': ['USA'], 'Year': [2000], 'Value': [100]})
        mock_pipeline.apply_filters.return_value = df
        mock_charts.year_line.return_value = Mock()
        mock_charts.year_bar.return_value = Mock()
        mock_st.session_state.figures = []
        
        render_country_analysis(df, 'USA', 2000, 2020)
        
        mock_charts.year_line.assert_called_once()
        mock_charts.year_bar.assert_called_once()
    
    @patch('ui.views.st')
    @patch('ui.views.pipeline')
    def test_applies_country_filter(self, mock_pipeline, mock_st):
        df = pd.DataFrame({'Country Name': ['USA'], 'Value': [100]})
        mock_pipeline.apply_filters.return_value = df
        mock_st.session_state.figures = []
        
        render_country_analysis(df, 'USA', 2000, 2020)
        
        mock_pipeline.apply_filters.assert_called_once_with(
            df,
            country='USA',
            start_year=2000,
            end_year=2020
        )


class TestRenderExports:
    @patch('ui.views.st')
    @patch('ui.views.pipeline')
    @patch('ui.views.exports')
    def test_applies_all_filters(self, mock_exports, mock_pipeline, mock_st):
        df = pd.DataFrame({'Value': [100]})
        mock_pipeline.apply_filters.return_value = df
        mock_st.columns.return_value = [Mock(), Mock(), Mock()]
        
        render_exports(df, 'Asia', 'China', 2000, 2020)
        
        mock_pipeline.apply_filters.assert_called_once_with(
            df,
            region='Asia',
            country='China',
            start_year=2000,
            end_year=2020
        )
    
    @patch('ui.views.st')
    @patch('ui.views.pipeline')
    @patch('ui.views.exports')
    def test_calls_csv_export(self, mock_exports, mock_pipeline, mock_st):
        df = pd.DataFrame({'Value': [100]})
        mock_pipeline.apply_filters.return_value = df
        mock_st.columns.return_value = [Mock(), Mock(), Mock()]
        
        render_exports(df, None, None, 2000, 2020)
        
        mock_exports.export_filtered_csv.assert_called_once()
    
    @patch('ui.views.st')
    @patch('ui.views.pipeline')
    @patch('ui.views.exports')
    def test_calls_charts_export(self, mock_exports, mock_pipeline, mock_st):
        df = pd.DataFrame({'Value': [100]})
        mock_pipeline.apply_filters.return_value = df
        mock_st.columns.return_value = [Mock(), Mock(), Mock()]
        
        render_exports(df, None, None, 2000, 2020)
        
        mock_exports.export_charts_as_png.assert_called_once()