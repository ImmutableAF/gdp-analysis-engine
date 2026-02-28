import pandas as pd
import pytest
from src.core.metadata import (
    extract_column,
    normalize_strings,
    get_all_regions,
    get_all_countries,
    get_year_range,
    get_valid_attr,
    get_metadata,
    DEFAULT_YEAR_RANGE,
)


def make_long_df():
    return pd.DataFrame({
        "Country Name": ["United States", "Germany", "France", "Germany"],
        "Continent":    ["Americas", "Europe", "Europe", "Europe"],
        "Year":         [1960, 1960, 1961, 1961],
        "Value":        [1000.0, 500.0, 300.0, 600.0],
    })


# ── ExtractColumn ────────────────────────────────────────────────────────────

class TestExtractColumn:

    def test_existing_column_is_returned(self):
        df = make_long_df()
        result = extract_column(df, "Country Name")
        assert list(result) == list(df["Country Name"])

    def test_missing_column_returns_empty_series(self):
        df = make_long_df()
        result = extract_column(df, "NonExistent")
        assert isinstance(result, pd.Series)
        assert len(result) == 0

    def test_missing_column_has_object_dtype(self):
        df = make_long_df()
        result = extract_column(df, "NonExistent")
        assert result.dtype == object

    def test_original_df_is_not_modified(self):
        df = make_long_df()
        _ = extract_column(df, "Country Name")
        assert list(df.columns) == ["Country Name", "Continent", "Year", "Value"]


# ── NormalizeStrings ─────────────────────────────────────────────────────────

class TestNormalizeStrings:

    def test_strings_are_title_cased(self):
        series = pd.Series(["united states", "germany"])
        result = normalize_strings(series)
        assert "United States" in result
        assert "Germany" in result

    def test_duplicates_are_removed(self):
        series = pd.Series(["Europe", "Europe", "Americas"])
        result = normalize_strings(series)
        assert result.count("Europe") == 1

    def test_nan_values_are_dropped(self):
        series = pd.Series(["Europe", float("nan"), "Americas"])
        result = normalize_strings(series)
        assert len(result) == 2
        assert all(isinstance(v, str) for v in result)

    def test_returns_a_list(self):
        series = pd.Series(["Europe", "Americas"])
        result = normalize_strings(series)
        assert isinstance(result, list)

    def test_empty_series_returns_empty_list(self):
        result = normalize_strings(pd.Series(dtype=object))
        assert result == []


# ── GetAllRegions ─────────────────────────────────────────────────────────────

class TestGetAllRegions:

    def test_returns_unique_continents(self):
        df = make_long_df()
        result = get_all_regions(df)
        assert sorted(result) == ["Americas", "Europe"]

    def test_values_are_title_cased(self):
        df = pd.DataFrame({"Continent": ["europe", "americas"]})
        result = get_all_regions(df)
        assert "Europe" in result
        assert "Americas" in result

    def test_missing_continent_column_returns_empty_list(self):
        df = pd.DataFrame({"Country Name": ["USA"]})
        result = get_all_regions(df)
        assert result == []

    def test_original_df_is_not_modified(self):
        df = make_long_df()
        original_columns = list(df.columns)
        _ = get_all_regions(df)
        assert list(df.columns) == original_columns


# ── GetAllCountries ───────────────────────────────────────────────────────────

class TestGetAllCountries:

    def test_returns_unique_countries(self):
        df = make_long_df()
        result = get_all_countries(df)
        assert sorted(result) == ["France", "Germany", "United States"]

    def test_values_are_title_cased(self):
        df = pd.DataFrame({"Country Name": ["united states", "germany"]})
        result = get_all_countries(df)
        assert "United States" in result
        assert "Germany" in result

    def test_missing_country_column_returns_empty_list(self):
        df = pd.DataFrame({"Continent": ["Europe"]})
        result = get_all_countries(df)
        assert result == []

    def test_original_df_is_not_modified(self):
        df = make_long_df()
        original_len = len(df)
        _ = get_all_countries(df)
        assert len(df) == original_len


# ── GetYearRange ──────────────────────────────────────────────────────────────

class TestGetYearRange:

    def test_returns_min_and_max_year(self):
        df = make_long_df()
        result = get_year_range(df)
        assert result == (1960, 1961)

    def test_returns_integers(self):
        df = make_long_df()
        min_year, max_year = get_year_range(df)
        assert isinstance(min_year, int)
        assert isinstance(max_year, int)

    def test_missing_year_column_falls_back_to_default(self):
        df = pd.DataFrame({"Country Name": ["USA"]})
        result = get_year_range(df)
        assert result == DEFAULT_YEAR_RANGE

    def test_all_nan_years_falls_back_to_default(self):
        df = pd.DataFrame({"Year": [float("nan"), float("nan")]})
        result = get_year_range(df)
        assert result == DEFAULT_YEAR_RANGE

    def test_non_numeric_year_strings_are_ignored(self):
        df = pd.DataFrame({"Year": ["n/a", "n/a"]})
        result = get_year_range(df)
        assert result == DEFAULT_YEAR_RANGE

    def test_mixed_valid_and_invalid_years(self):
        df = pd.DataFrame({"Year": [1990, float("nan"), 2000]})
        result = get_year_range(df)
        assert result == (1990, 2000)

    def test_original_df_is_not_modified(self):
        df = make_long_df()
        original_years = list(df["Year"])
        _ = get_year_range(df)
        assert list(df["Year"]) == original_years


# ── GetValidAttr ──────────────────────────────────────────────────────────────

class TestGetValidAttr:

    def test_returns_tuple_of_two(self):
        df = make_long_df()
        result = get_valid_attr(df)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_first_element_is_regions_list(self):
        df = make_long_df()
        regions, _ = get_valid_attr(df)
        assert isinstance(regions, list)
        assert sorted(regions) == ["Americas", "Europe"]

    def test_second_element_is_year_range_tuple(self):
        df = make_long_df()
        _, year_range = get_valid_attr(df)
        assert year_range == (1960, 1961)

    def test_original_df_is_not_modified(self):
        df = make_long_df()
        original_len = len(df)
        _ = get_valid_attr(df)
        assert len(df) == original_len


# ── GetMetadata ───────────────────────────────────────────────────────────────

class TestGetMetadata:

    def test_returns_dict_with_expected_keys(self):
        df = make_long_df()
        result = get_metadata(df)
        assert set(result.keys()) == {"regions", "countries", "year_range"}

    def test_regions_are_sorted(self):
        df = make_long_df()
        result = get_metadata(df)
        assert result["regions"] == sorted(result["regions"])

    def test_countries_are_sorted(self):
        df = make_long_df()
        result = get_metadata(df)
        assert result["countries"] == sorted(result["countries"])

    def test_year_range_is_correct(self):
        df = make_long_df()
        result = get_metadata(df)
        assert result["year_range"] == (1960, 1961)

    def test_all_countries_are_present(self):
        df = make_long_df()
        result = get_metadata(df)
        assert sorted(result["countries"]) == ["France", "Germany", "United States"]

    def test_all_regions_are_present(self):
        df = make_long_df()
        result = get_metadata(df)
        assert sorted(result["regions"]) == ["Americas", "Europe"]

    def test_original_df_is_not_modified(self):
        df = make_long_df()
        original_len = len(df)
        _ = get_metadata(df)
        assert len(df) == original_len