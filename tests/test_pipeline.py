# test_pipeline.py
import pytest
import pandas as pd
import numpy as np
from src.core.pipeline import (
    transform,
    filter_by_region,
    filter_by_country,
    filter_by_year,
    aggregate_by_region,
    aggregate_by_country,
    aggregate_by_country_code,
    aggregate_all,
    apply_filters,
    run_pipeline
)
from src.core.config_manager.config_models import QueryConfig


class TestTransform:
    def test_wide_to_long_format(self):
        df = pd.DataFrame({
            'Country Name': ['USA'],
            'Continent': ['North America'],
            'Indicator Name': ['GDP'],
            'Indicator Code': ['NY.GDP'],
            'Country Code': ['US'],
            '1960': [100],
            '1961': [200]
        })
        result = transform(df)
        
        assert 'Year' in result.columns
        assert 'Value' in result.columns
        assert len(result) == 2
        assert result['Year'].dtype == int
    
    def test_year_as_integer(self):
        df = pd.DataFrame({
            'Country Name': ['USA'],
            'Continent': ['NA'],
            'Indicator Name': ['GDP'],
            'Indicator Code': ['GDP'],
            'Country Code': ['US'],
            '2000': [100]
        })
        result = transform(df)
        
        assert result['Year'].iloc[0] == 2000
        assert isinstance(result['Year'].iloc[0], (int, np.integer))
    
    def test_preserves_id_vars(self):
        df = pd.DataFrame({
            'Country Name': ['USA', 'UK'],
            'Continent': ['NA', 'EU'],
            'Indicator Name': ['GDP', 'GDP'],
            'Indicator Code': ['GDP', 'GDP'],
            'Country Code': ['US', 'GB'],
            '2000': [100, 200]
        })
        result = transform(df)
        
        assert 'Country Name' in result.columns
        assert 'Continent' in result.columns
        assert 'Indicator Name' in result.columns


class TestFilterByRegion:
    def test_filters_matching_region(self):
        df = pd.DataFrame({
            'Continent': ['Asia', 'Europe', 'Asia'],
            'Value': [100, 200, 300]
        })
        result = filter_by_region(df, 'Asia')
        
        assert len(result) == 2
        assert all(result['Continent'] == 'Asia')
    
    def test_case_insensitive(self):
        df = pd.DataFrame({
            'Continent': ['Asia', 'Europe'],
            'Value': [100, 200]
        })
        result = filter_by_region(df, 'ASIA')
        
        assert len(result) == 1
    
    def test_none_returns_copy(self):
        df = pd.DataFrame({'Continent': ['Asia'], 'Value': [100]})
        result = filter_by_region(df, None)
        
        assert len(result) == len(df)
        assert result is not df


class TestFilterByCountry:
    def test_filters_matching_country(self):
        df = pd.DataFrame({
            'Country Name': ['USA', 'UK', 'USA'],
            'Value': [100, 200, 300]
        })
        result = filter_by_country(df, 'USA')
        
        assert len(result) == 2
        assert all(result['Country Name'] == 'USA')
    
    def test_case_insensitive(self):
        df = pd.DataFrame({
            'Country Name': ['USA'],
            'Value': [100]
        })
        result = filter_by_country(df, 'usa')
        
        assert len(result) == 1
    
    def test_none_returns_copy(self):
        df = pd.DataFrame({'Country Name': ['USA'], 'Value': [100]})
        result = filter_by_country(df, None)
        
        assert len(result) == len(df)


class TestFilterByYear:
    def test_single_year(self):
        df = pd.DataFrame({
            'Year': [2000, 2001, 2002],
            'Value': [100, 200, 300]
        })
        result = filter_by_year(df, 2001, None)
        
        assert len(result) == 1
        assert result['Year'].iloc[0] == 2001
    
    def test_year_range(self):
        df = pd.DataFrame({
            'Year': [2000, 2001, 2002, 2003],
            'Value': [100, 200, 300, 400]
        })
        result = filter_by_year(df, 2001, 2002)
        
        assert len(result) == 2
        assert set(result['Year']) == {2001, 2002}
    
    def test_none_returns_copy(self):
        df = pd.DataFrame({'Year': [2000], 'Value': [100]})
        result = filter_by_year(df, None, None)
        
        assert len(result) == len(df)
    
    def test_only_end_year(self):
        df = pd.DataFrame({
            'Year': [2000, 2001, 2002],
            'Value': [100, 200, 300]
        })
        result = filter_by_year(df, None, 2002)
        
        assert len(result) == 1
        assert result['Year'].iloc[0] == 2002


class TestAggregateByRegion:
    def test_sum_operation(self):
        df = pd.DataFrame({
            'Continent': ['Asia', 'Asia', 'Europe'],
            'Value': [100, 200, 300]
        })
        result = aggregate_by_region(df, 'sum')
        
        assert len(result) == 2
        assert result[result['Continent'] == 'Asia']['Value'].iloc[0] == 300
    
    def test_mean_operation(self):
        df = pd.DataFrame({
            'Continent': ['Asia', 'Asia', 'Europe'],
            'Value': [100, 200, 300]
        })
        result = aggregate_by_region(df, 'avg')
        
        assert result[result['Continent'] == 'Asia']['Value'].iloc[0] == 150


class TestAggregateByCountry:
    def test_sum_operation(self):
        df = pd.DataFrame({
            'Country Name': ['USA', 'USA', 'UK'],
            'Value': [100, 200, 300]
        })
        result = aggregate_by_country(df, 'sum')
        
        assert result[result['Country Name'] == 'USA']['Value'].iloc[0] == 300
    
    def test_mean_operation(self):
        df = pd.DataFrame({
            'Country Name': ['USA', 'USA'],
            'Value': [100, 200]
        })
        result = aggregate_by_country(df, 'avg')
        
        assert result['Value'].iloc[0] == 150


class TestAggregateByCountryCode:
    def test_sum_operation(self):
        df = pd.DataFrame({
            'Country Code': ['US', 'US', 'GB'],
            'Value': [100, 200, 300]
        })
        result = aggregate_by_country_code(df, 'sum')
        
        assert result[result['Country Code'] == 'US']['Value'].iloc[0] == 300


class TestAggregateAll:
    def test_sum_operation(self):
        df = pd.DataFrame({
            'Country Name': ['USA'],
            'Country Code': ['US'],
            'Indicator Name': ['GDP'],
            'Indicator Code': ['NY.GDP'],
            'Continent': ['NA'],
            'Value': [100, 200]
        })
        result = aggregate_all(df, 'sum')
        
        assert 'Operation' in result.columns
        assert result['Operation'].iloc[0] == 'Sum'
    
    def test_avg_operation(self):
        df = pd.DataFrame({
            'Country Name': ['USA'],
            'Country Code': ['US'],
            'Indicator Name': ['GDP'],
            'Indicator Code': ['NY.GDP'],
            'Continent': ['NA'],
            'Value': [100, 200]
        })
        result = aggregate_all(df, 'avg')
        
        assert result['Operation'].iloc[0] == 'Average'
    
    def test_case_insensitive(self):
        df = pd.DataFrame({
            'Country Name': ['USA'],
            'Country Code': ['US'],
            'Indicator Name': ['GDP'],
            'Indicator Code': ['NY.GDP'],
            'Continent': ['NA'],
            'Value': [100]
        })
        result = aggregate_all(df, 'SUM')
        
        assert 'Operation' in result.columns


class TestApplyFilters:
    def test_multiple_filters(self):
        df = pd.DataFrame({
            'Continent': ['Asia', 'Asia', 'Europe'],
            'Country Name': ['China', 'India', 'France'],
            'Year': [2000, 2000, 2000],
            'Value': [100, 200, 300]
        })
        result = apply_filters(df, region='Asia', start_year=2000, end_year=2000)
        
        assert len(result) == 2
        assert all(result['Continent'] == 'Asia')
    
    def test_drops_nan_values(self):
        df = pd.DataFrame({
            'Continent': ['Asia'],
            'Value': [np.nan, 100]
        })
        result = apply_filters(df)
        
        assert len(result) == 1


class TestRunPipeline:
    def test_full_pipeline_execution(self, capsys):
        df = pd.DataFrame({
            'Country Name': ['USA'],
            'Continent': ['NA'],
            'Indicator Name': ['GDP'],
            'Indicator Code': ['NY.GDP'],
            'Country Code': ['US'],
            '2000': [100],
            '2001': [200]
        })
        config = QueryConfig(region='NA', country='USA', startYear=2000, endYear=2001, operation='sum')
        
        run_pipeline(df, config)
        captured = capsys.readouterr()
        
        assert len(captured.out) > 0