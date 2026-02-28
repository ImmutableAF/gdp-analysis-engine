import pandas as pd
import pytest
from src.core.data_cleaning import (
    convert_years_to_numeric,
    fill_missing_years,
    remove_invalid_values,
    drop_duplicates,
    clean_gdp_data,
)


def make_raw_df():
    return pd.DataFrame({
        "Country Name":   ["USA", "USA", "Germany", "France"],
        "Indicator Code": ["NY.GDP.MKTP.CD"] * 4,
        "1960": ["1000", "N/A", "500",  "-200"],
        "1961": ["1100", "N/A", None,   "300"],
        "1962": ["1200", "N/A", "600",  "400"],
    })


class TestConvertYearsToNumeric:

    def test_strings_become_numeric(self):
        df = make_raw_df()
        result = convert_years_to_numeric(df, start_year=1960, end_year=1962)
        assert pd.api.types.is_numeric_dtype(result["1960"])
        assert result["1960"].iloc[0] == 1000

    def test_unparseable_strings_become_nan(self):
        df = make_raw_df()
        result = convert_years_to_numeric(df, start_year=1960, end_year=1962)
        assert pd.isna(result["1960"].iloc[1])

    def test_original_df_is_not_modified(self):
        df = make_raw_df()
        _ = convert_years_to_numeric(df, start_year=1960, end_year=1962)
        assert df["1960"].iloc[0] == "1000"


class TestFillMissingYears:

    def test_ffill_propagates_forward(self):
        df = pd.DataFrame({
            "Country Name":   ["USA"],
            "Indicator Code": ["NY.GDP.MKTP.CD"],
            "1960": [100.0],
            "1961": [float("nan")],
            "1962": [float("nan")],
        })
        result = fill_missing_years(df, method="ffill", start_year=1960, end_year=1962)
        assert result["1961"].iloc[0] == 100.0
        assert result["1962"].iloc[0] == 100.0

    def test_bfill_propagates_backward(self):
        df = pd.DataFrame({
            "Country Name":   ["USA"],
            "Indicator Code": ["NY.GDP.MKTP.CD"],
            "1960": [float("nan")],
            "1961": [float("nan")],
            "1962": [300.0],
        })
        result = fill_missing_years(df, method="bfill", start_year=1960, end_year=1962)
        assert result["1960"].iloc[0] == 300.0
        assert result["1961"].iloc[0] == 300.0

    def test_zero_replaces_nan_with_zero(self):
        df = pd.DataFrame({
            "Country Name":   ["USA"],
            "Indicator Code": ["NY.GDP.MKTP.CD"],
            "1960": [float("nan")],
            "1961": [200.0],
            "1962": [float("nan")],
        })
        result = fill_missing_years(df, method="zero", start_year=1960, end_year=1962)
        assert result["1960"].iloc[0] == 0.0
        assert result["1962"].iloc[0] == 0.0

    def test_invalid_method_leaves_data_unchanged(self):
        df = pd.DataFrame({
            "Country Name":   ["USA"],
            "Indicator Code": ["NY.GDP.MKTP.CD"],
            "1960": [float("nan")],
            "1961": [200.0],
            "1962": [float("nan")],
        })
        result = fill_missing_years(df, method="abc", start_year=1960, end_year=1962)
        assert pd.isna(result["1960"].iloc[0])
        assert pd.isna(result["1962"].iloc[0])

    def test_original_df_is_not_modified(self):
        df = pd.DataFrame({
            "Country Name":   ["USA"],
            "Indicator Code": ["NY.GDP.MKTP.CD"],
            "1960": [float("nan")],
            "1961": [200.0],
            "1962": [float("nan")],
        })
        _ = fill_missing_years(df, method="ffill", start_year=1960, end_year=1962)
        assert pd.isna(df["1960"].iloc[0])


class TestRemoveInvalidValues:

    def test_negative_values_become_nan(self):
        df = pd.DataFrame({
            "Country Name":   ["France"],
            "Indicator Code": ["NY.GDP.MKTP.CD"],
            "1960": [-200.0],
            "1961": [300.0],
        })
        result = remove_invalid_values(df, start_year=1960, end_year=1961)
        assert pd.isna(result["1960"].iloc[0])

    def test_positive_values_are_untouched(self):
        df = pd.DataFrame({
            "Country Name":   ["France"],
            "Indicator Code": ["NY.GDP.MKTP.CD"],
            "1960": [300.0],
            "1961": [400.0],
        })
        result = remove_invalid_values(df, start_year=1960, end_year=1961)
        assert result["1960"].iloc[0] == 300.0

    def test_zero_is_untouched(self):
        df = pd.DataFrame({
            "Country Name":   ["France"],
            "Indicator Code": ["NY.GDP.MKTP.CD"],
            "1960": [0.0],
            "1961": [400.0],
        })
        result = remove_invalid_values(df, start_year=1960, end_year=1961)
        assert result["1960"].iloc[0] == 0.0

    def test_existing_nan_stays_nan(self):
        df = pd.DataFrame({
            "Country Name":   ["Germany"],
            "Indicator Code": ["NY.GDP.MKTP.CD"],
            "1960": [float("nan")],
            "1961": [500.0],
        })
        result = remove_invalid_values(df, start_year=1960, end_year=1961)
        assert pd.isna(result["1960"].iloc[0])

    def test_original_df_is_not_modified(self):
        df = pd.DataFrame({
            "Country Name":   ["France"],
            "Indicator Code": ["NY.GDP.MKTP.CD"],
            "1960": [-200.0],
            "1961": [300.0],
        })
        _ = remove_invalid_values(df, start_year=1960, end_year=1961)
        assert df["1960"].iloc[0] == -200.0


class TestDropDuplicates:

    def test_duplicate_country_indicator_is_removed(self):
        df = make_raw_df()
        result = drop_duplicates(df)
        usa_rows = result[result["Country Name"] == "USA"]
        assert len(usa_rows) == 1

    def test_unique_rows_are_kept(self):
        df = make_raw_df()
        result = drop_duplicates(df)
        assert "Germany" in result["Country Name"].values
        assert "France" in result["Country Name"].values

    def test_row_count_is_reduced(self):
        df = make_raw_df()
        result = drop_duplicates(df)
        assert len(result) < len(df)

    def test_original_df_is_not_modified(self):
        df = make_raw_df()
        _ = drop_duplicates(df)
        assert len(df) == 4


class TestCleanGdpData:

    def test_returns_dataframe(self):
        df = make_raw_df()
        result = clean_gdp_data(df, fill_method="ffill")
        assert isinstance(result, pd.DataFrame)

    def test_no_duplicates_in_output(self):
        df = make_raw_df()
        result = clean_gdp_data(df, fill_method="ffill")
        assert len(result) == len(result.drop_duplicates(subset=["Country Name", "Indicator Code"]))

    def test_no_negative_values_in_output(self):
        df = make_raw_df()
        result = clean_gdp_data(df, fill_method="zero")
        for col in ["1960", "1961", "1962"]:
            assert (result[col].dropna() >= 0).all()

    def test_year_columns_are_numeric(self):
        df = make_raw_df()
        result = clean_gdp_data(df, fill_method="ffill")
        for col in ["1960", "1961", "1962"]:
            assert pd.api.types.is_numeric_dtype(result[col])

    def test_original_df_is_not_modified(self):
        df = make_raw_df()
        _ = clean_gdp_data(df, fill_method="ffill")
        assert df["1960"].iloc[0] == "1000"