# test_handle.py
import pytest
import pandas as pd
import numpy as np
from src.core.handle import get_all_regions, get_all_countries, get_year_range


class TestGetAllRegions:
    def test_extracts_unique_regions(self):
        df = pd.DataFrame({
            'Continent': ['Asia', 'Europe', 'Asia', 'Africa']
        })
        result = get_all_regions(df)
        
        assert set(result) == {'Asia', 'Europe', 'Africa'}
        assert len(result) == 3
    
    def test_title_case_conversion(self):
        df = pd.DataFrame({
            'Continent': ['asia', 'EUROPE', 'AfRiCa']
        })
        result = get_all_regions(df)
        
        assert 'Asia' in result
        assert 'Europe' in result
        assert 'Africa' in result
    
    def test_drops_nan_values(self):
        df = pd.DataFrame({
            'Continent': ['Asia', np.nan, 'Europe', None]
        })
        result = get_all_regions(df)
        
        assert len(result) == 2
        assert set(result) == {'Asia', 'Europe'}
    
    def test_missing_continent_column(self):
        df = pd.DataFrame({
            'Country': ['USA', 'UK']
        })
        result = get_all_regions(df)
        
        assert result == []
    
    def test_empty_dataframe(self):
        df = pd.DataFrame()
        result = get_all_regions(df)
        
        assert result == []
    
    def test_all_nan_continent(self):
        df = pd.DataFrame({
            'Continent': [np.nan, np.nan, np.nan]
        })
        result = get_all_regions(df)
        
        assert result == []


class TestGetAllCountries:
    def test_extracts_unique_countries(self):
        df = pd.DataFrame({
            'Country Name': ['USA', 'UK', 'USA', 'France']
        })
        result = get_all_countries(df)
        
        assert set(result) == {'Usa', 'Uk', 'France'}
        assert len(result) == 3
    
    def test_title_case_conversion(self):
        df = pd.DataFrame({
            'Country Name': ['united states', 'UNITED KINGDOM', 'FrAnCe']
        })
        result = get_all_countries(df)
        
        assert 'United States' in result
        assert 'United Kingdom' in result
        assert 'France' in result
    
    def test_drops_nan_values(self):
        df = pd.DataFrame({
            'Country Name': ['USA', np.nan, 'UK', None]
        })
        result = get_all_countries(df)
        
        assert len(result) == 2
        assert set(result) == {'Usa', 'Uk'}
    
    def test_missing_country_column(self):
        df = pd.DataFrame({
            'Region': ['Asia', 'Europe']
        })
        result = get_all_countries(df)
        
        assert result == []
    
    def test_empty_dataframe(self):
        df = pd.DataFrame()
        result = get_all_countries(df)
        
        assert result == []


class TestGetYearRange:
    def test_extracts_min_max_years(self):
        df = pd.DataFrame({
            'Year': [1990, 2000, 1995, 2020, 1980]
        })
        result = get_year_range(df)
        
        assert result == (1980, 2020)
    
    def test_single_year(self):
        df = pd.DataFrame({
            'Year': [2000, 2000, 2000]
        })
        result = get_year_range(df)
        
        assert result == (2000, 2000)
    
    def test_string_years_converted(self):
        df = pd.DataFrame({
            'Year': ['1990', '2000', '1995']
        })
        result = get_year_range(df)
        
        assert result == (1990, 2000)
    
    def test_mixed_valid_invalid_years(self):
        df = pd.DataFrame({
            'Year': [1990, 'invalid', 2000, np.nan, 1995]
        })
        result = get_year_range(df)
        
        assert result == (1990, 2000)
    
    def test_missing_year_column(self):
        df = pd.DataFrame({
            'Country': ['USA', 'UK']
        })
        result = get_year_range(df)
        
        assert result == (1960, 2024)
    
    def test_empty_dataframe(self):
        df = pd.DataFrame()
        result = get_year_range(df)
        
        assert result == (1960, 2024)
    
    def test_empty_year_column(self):
        df = pd.DataFrame({
            'Year': []
        })
        result = get_year_range(df)
        
        assert result == (1960, 2024)
    
    def test_all_invalid_years(self):
        df = pd.DataFrame({
            'Year': ['invalid', np.nan, 'abc']
        })
        result = get_year_range(df)
        
        assert result == (1960, 2024)
    
    def test_returns_integers(self):
        df = pd.DataFrame({
            'Year': [1990.5, 2000.9]
        })
        result = get_year_range(df)
        
        assert isinstance(result[0], int)
        assert isinstance(result[1], int)