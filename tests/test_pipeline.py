# tests/test_pipeline.py
import pytest
import pandas as pd
from pipeline.transform import transform_raw_gdp
from pipeline.filter import filter_data
from config_core.config_models import QueryConfig

def test_transform_raw_gdp():
    # Sample data
    df = pd.DataFrame({
        'Country Name': ['USA', 'Canada'],
        'Continent': ['North America', 'North America'],
        '2020': [20000, 1500],
        '2021': [21000, 1600]
    })
    
    result = transform_raw_gdp(df)
    
    assert 'Region' in result.columns
    assert 'Continent' not in result.columns
    assert 'Year' in result.columns
    assert len(result) == 4  # 2 countries * 2 years

def test_filter_by_region():
    df = pd.DataFrame({
        'Country Name': ['USA', 'France'],
        'Region': ['North America', 'Europe'],
        'Year': [2020, 2020],
        'Value': [20000, 3000]
    })
    
    config = QueryConfig(
        region='Europe',
        year=None,
        country=None,
        operation='average',
        dashboard_charts=[]
    )
    
    result = filter_data(df, config)
    assert len(result) == 1
    assert result.iloc[0]['Country Name'] == 'France'