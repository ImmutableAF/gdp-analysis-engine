# test_data_cleaning.py
import pytest
import pandas as pd
import numpy as np
from src.core.data_cleaning import (
    convert_years_to_numeric,
    fill_missing_years,
    remove_invalid_values,
    drop_duplicates,
    clean_gdp_data
)


class TestConvertYearsToNumeric:
    def test_converts_valid_years(self):
        df = pd.DataFrame({
            'Country Name': ['A', 'B'],
            '1960': ['100', '200'],
            '1961': ['150', '250']
        })
        result = convert_years_to_numeric(df, 1960, 1961)
        
        assert result['1960'].dtype in [np.float64, np.int64]
        assert result['1961'].dtype in [np.float64, np.int64]
        assert result.loc[0, '1960'] == 100
        assert result.loc[1, '1961'] == 250
    
    def test_non_convertible_becomes_nan(self):
        df = pd.DataFrame({
            '1960': ['100', 'invalid', '300'],
            '1961': ['abc', '200', 'xyz']
        })
        result = convert_years_to_numeric(df, 1960, 1961)
        
        assert pd.isna(result.loc[1, '1960'])
        assert pd.isna(result.loc[0, '1961'])
        assert pd.isna(result.loc[2, '1961'])
    
    def test_original_dataframe_unchanged(self):
        df = pd.DataFrame({'1960': ['100', '200']})
        original = df.copy()
        convert_years_to_numeric(df, 1960, 1960)
        
        pd.testing.assert_frame_equal(df, original)
    
    def test_year_range_filtering(self):
        df = pd.DataFrame({
            '1960': ['100'],
            '1961': ['200'],
            '1962': ['300']
        })
        result = convert_years_to_numeric(df, 1960, 1961)
        
        assert result['1960'].dtype in [np.float64, np.int64]
        assert result['1961'].dtype in [np.float64, np.int64]
        assert result['1962'].dtype == object
    
    def test_empty_dataframe(self):
        df = pd.DataFrame()
        result = convert_years_to_numeric(df, 1960, 2024)
        assert result.empty


class TestFillMissingYears:
    def test_fill_with_zero(self):
        df = pd.DataFrame({
            '1960': [100.0, np.nan, 300.0],
            '1961': [np.nan, 200.0, np.nan]
        })
        result = fill_missing_years(df, method='zero', start_year=1960, end_year=1961)
        
        assert result.loc[1, '1960'] == 0
        assert result.loc[0, '1961'] == 0
        assert result.loc[2, '1961'] == 0
    
    def test_fill_with_ffill(self):
        df = pd.DataFrame({
            '1960': [100.0, 200.0],
            '1961': [np.nan, np.nan],
            '1962': [300.0, 400.0]
        })
        result = fill_missing_years(df, method='ffill', start_year=1960, end_year=1962)
        
        assert result.loc[0, '1961'] == 100.0
        assert result.loc[1, '1961'] == 200.0
    
    def test_fill_with_bfill(self):
        df = pd.DataFrame({
            '1960': [100.0, 200.0],
            '1961': [np.nan, np.nan],
            '1962': [300.0, 400.0]
        })
        result = fill_missing_years(df, method='bfill', start_year=1960, end_year=1962)
        
        assert result.loc[0, '1961'] == 300.0
        assert result.loc[1, '1961'] == 400.0
    
    def test_original_unchanged(self):
        df = pd.DataFrame({'1960': [100.0, np.nan]})
        original = df.copy()
        fill_missing_years(df, method='zero', start_year=1960, end_year=1960)
        
        pd.testing.assert_frame_equal(df, original)
    
    def test_no_missing_values(self):
        df = pd.DataFrame({
            '1960': [100.0, 200.0],
            '1961': [150.0, 250.0]
        })
        result = fill_missing_years(df, method='zero', start_year=1960, end_year=1961)
        
        pd.testing.assert_frame_equal(result, df)


class TestRemoveInvalidValues:
    def test_negative_values_to_nan(self):
        df = pd.DataFrame({
            '1960': [100.0, -50.0, 200.0],
            '1961': [-100.0, 150.0, -200.0]
        })
        result = remove_invalid_values(df, 1960, 1961)
        
        assert pd.isna(result.loc[1, '1960'])
        assert pd.isna(result.loc[0, '1961'])
        assert pd.isna(result.loc[2, '1961'])
    
    def test_positive_values_preserved(self):
        df = pd.DataFrame({
            '1960': [100.0, 200.0, 300.0],
            '1961': [150.0, 250.0, 350.0]
        })
        result = remove_invalid_values(df, 1960, 1961)
        
        pd.testing.assert_frame_equal(result, df)
    
    def test_zero_values_preserved(self):
        df = pd.DataFrame({
            '1960': [0.0, 100.0],
            '1961': [200.0, 0.0]
        })
        result = remove_invalid_values(df, 1960, 1961)
        
        assert result.loc[0, '1960'] == 0.0
        assert result.loc[1, '1961'] == 0.0
    
    def test_existing_nan_preserved(self):
        df = pd.DataFrame({
            '1960': [100.0, np.nan, -50.0],
            '1961': [np.nan, 200.0, 300.0]
        })
        result = remove_invalid_values(df, 1960, 1961)
        
        assert pd.isna(result.loc[1, '1960'])
        assert pd.isna(result.loc[0, '1961'])
    
    def test_original_unchanged(self):
        df = pd.DataFrame({'1960': [100.0, -50.0]})
        original = df.copy()
        remove_invalid_values(df, 1960, 1960)
        
        pd.testing.assert_frame_equal(df, original)


class TestDropDuplicates:
    def test_removes_exact_duplicates(self):
        df = pd.DataFrame({
            'Country Name': ['USA', 'USA', 'UK'],
            'Indicator Code': ['GDP', 'GDP', 'GDP'],
            '1960': [100, 100, 200]
        })
        result = drop_duplicates(df)
        
        assert len(result) == 2
        assert result['Country Name'].tolist() == ['USA', 'UK']
    
    def test_keeps_different_indicators(self):
        df = pd.DataFrame({
            'Country Name': ['USA', 'USA'],
            'Indicator Code': ['GDP', 'POP'],
            '1960': [100, 200]
        })
        result = drop_duplicates(df)
        
        assert len(result) == 2
    
    def test_keeps_different_countries(self):
        df = pd.DataFrame({
            'Country Name': ['USA', 'UK'],
            'Indicator Code': ['GDP', 'GDP'],
            '1960': [100, 200]
        })
        result = drop_duplicates(df)
        
        assert len(result) == 2
    
    def test_no_duplicates(self):
        df = pd.DataFrame({
            'Country Name': ['USA', 'UK', 'FR'],
            'Indicator Code': ['GDP', 'GDP', 'GDP'],
            '1960': [100, 200, 300]
        })
        result = drop_duplicates(df)
        
        assert len(result) == 3
    
    def test_empty_dataframe(self):
        df = pd.DataFrame(columns=['Country Name', 'Indicator Code'])
        result = drop_duplicates(df)
        assert result.empty


class TestCleanGdpData:
    def test_full_pipeline_ffill(self):
        df = pd.DataFrame({
            'Country Name': ['USA', 'USA', 'UK'],
            'Indicator Code': ['GDP', 'GDP', 'GDP'],
            '1960': ['100', '100', '-50'],
            '1961': ['invalid', '200', '300']
        })
        result = clean_gdp_data(df, fill_method='ffill')
        
        assert len(result) == 2
        assert pd.isna(result.iloc[0]['1961']) or result.iloc[0]['1961'] == 100.0
        assert pd.isna(result[result['Country Name'] == 'UK'].iloc[0]['1960'])
    
    def test_full_pipeline_zero(self):
        df = pd.DataFrame({
            'Country Name': ['USA'],
            'Indicator Code': ['GDP'],
            '1960': ['100'],
            '1961': [np.nan]
        })
        result = clean_gdp_data(df, fill_method='zero')
        
        assert result.loc[0, '1961'] == 0.0
    
    def test_full_pipeline_bfill(self):
        df = pd.DataFrame({
            'Country Name': ['USA'],
            'Indicator Code': ['GDP'],
            '1960': [np.nan],
            '1961': ['200']
        })
        result = clean_gdp_data(df, fill_method='bfill')
        
        assert result.loc[0, '1960'] == 200.0
    
    def test_pipeline_order_matters(self):
        df = pd.DataFrame({
            'Country Name': ['USA', 'USA'],
            'Indicator Code': ['GDP', 'GDP'],
            '1960': ['-100', '200']
        })
        result = clean_gdp_data(df)
        
        assert len(result) == 1
        assert pd.isna(result.iloc[0]['1960']) or result.iloc[0]['1960'] > 0