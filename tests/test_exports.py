# test_exports.py
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from src.ui.exports import export_filtered_csv, export_charts_as_png


class TestExportFilteredCsv:
    @patch('ui.exports.st')
    def test_exports_non_empty_dataframe(self, mock_st):
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        
        export_filtered_csv(df, "test.csv")
        
        mock_st.download_button.assert_called_once()
        call_args = mock_st.download_button.call_args
        
        assert call_args[1]['file_name'] == "test.csv"
        assert call_args[1]['mime'] == "text/csv"
        assert call_args[1]['disabled'] is False
    
    @patch('ui.exports.st')
    def test_disabled_for_empty_dataframe(self, mock_st):
        df = pd.DataFrame()
        
        export_filtered_csv(df)
        
        call_args = mock_st.download_button.call_args
        assert call_args[1]['disabled'] is True
    
    @patch('ui.exports.st')
    def test_default_filename(self, mock_st):
        df = pd.DataFrame({'A': [1]})
        
        export_filtered_csv(df)
        
        call_args = mock_st.download_button.call_args
        assert call_args[1]['file_name'] == "filtered_data.csv"
    
    @patch('ui.exports.st')
    def test_custom_filename(self, mock_st):
        df = pd.DataFrame({'A': [1]})
        
        export_filtered_csv(df, "custom.csv")
        
        call_args = mock_st.download_button.call_args
        assert call_args[1]['file_name'] == "custom.csv"
    
    @patch('ui.exports.st')
    def test_csv_content_format(self, mock_st):
        df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        
        export_filtered_csv(df)
        
        call_args = mock_st.download_button.call_args
        csv_data = call_args[0][1]
        
        assert 'A,B' in csv_data
        assert '1,3' in csv_data
    
    @patch('ui.exports.st')
    def test_help_text_when_empty(self, mock_st):
        df = pd.DataFrame()
        
        export_filtered_csv(df)
        
        call_args = mock_st.download_button.call_args
        assert call_args[1]['help'] == "No data available for export"
    
    @patch('ui.exports.st')
    def test_no_help_text_when_ready(self, mock_st):
        df = pd.DataFrame({'A': [1]})
        
        export_filtered_csv(df)
        
        call_args = mock_st.download_button.call_args
        assert call_args[1]['help'] is None


class TestExportChartsAsPng:
    @patch('ui.exports.st')
    def test_initializes_session_state(self, mock_st):
        mock_st.session_state = {}
        
        export_charts_as_png()
        
        assert 'charts_zip' in mock_st.session_state
        assert 'charts_ready' in mock_st.session_state
    
    @patch('ui.exports.st')
    def test_generates_button_disabled_when_no_figures(self, mock_st):
        mock_st.session_state = {'figures': []}
        mock_st.button.return_value = False
        mock_st.columns.return_value = [Mock(), Mock()]
        
        export_charts_as_png()
        
        button_calls = [call for call in mock_st.button.call_args_list if 'Generate' in str(call)]
        assert len(button_calls) > 0
        assert button_calls[0][1]['disabled'] is True
    
    @patch('ui.exports.st')
    def test_download_button_disabled_initially(self, mock_st):
        mock_st.session_state = {'figures': [], 'charts_ready': False}
        mock_st.button.return_value = False
        mock_st.columns.return_value = [Mock(), Mock()]
        
        export_charts_as_png()
        
        download_calls = [call for call in mock_st.download_button.call_args_list if 'Download' in str(call)]
        assert len(download_calls) > 0
        assert download_calls[0][1]['disabled'] is True
    
    @patch('ui.exports.st')
    def test_creates_zip_when_generate_clicked(self, mock_st):
        mock_fig = Mock()
        mock_fig.to_image.return_value = b'fake_png_data'
        
        mock_st.session_state = {
            'figures': [('chart1', mock_fig)],
            'charts_zip': None,
            'charts_ready': False
        }
        mock_st.button.return_value = True
        mock_st.columns.return_value = [Mock(), Mock()]
        mock_st.spinner.return_value.__enter__ = Mock()
        mock_st.spinner.return_value.__exit__ = Mock()
        
        export_charts_as_png()
        
        assert mock_st.session_state['charts_ready'] is True
        assert mock_st.session_state['charts_zip'] is not None
    
    @patch('ui.exports.st')
    def test_handles_export_failure(self, mock_st):
        mock_fig = Mock()
        mock_fig.to_image.side_effect = Exception("Kaleido error")
        
        mock_st.session_state = {
            'figures': [('chart1', mock_fig)],
            'charts_zip': None,
            'charts_ready': False
        }
        mock_st.button.return_value = True
        mock_st.columns.return_value = [Mock(), Mock()]
        mock_st.spinner.return_value.__enter__ = Mock()
        mock_st.spinner.return_value.__exit__ = Mock()
        
        export_charts_as_png()
        
        assert mock_st.session_state['charts_ready'] is False
        assert mock_st.session_state['charts_zip'] is None
        mock_st.error.assert_called_once()
    
    @patch('ui.exports.st')
    def test_multiple_figures_in_zip(self, mock_st):
        mock_fig1 = Mock()
        mock_fig1.to_image.return_value = b'png1'
        mock_fig2 = Mock()
        mock_fig2.to_image.return_value = b'png2'
        
        mock_st.session_state = {
            'figures': [('chart1', mock_fig1), ('chart2', mock_fig2)],
            'charts_zip': None,
            'charts_ready': False
        }
        mock_st.button.return_value = True
        mock_st.columns.return_value = [Mock(), Mock()]
        mock_st.spinner.return_value.__enter__ = Mock()
        mock_st.spinner.return_value.__exit__ = Mock()
        
        export_charts_as_png()
        
        zip_buffer = mock_st.session_state['charts_zip']
        assert zip_buffer is not None
    
    @patch('ui.exports.st')
    def test_uses_two_columns(self, mock_st):
        mock_st.session_state = {'figures': []}
        mock_st.columns.return_value = [Mock(), Mock()]
        
        export_charts_as_png()
        
        mock_st.columns.assert_called_once_with(2)