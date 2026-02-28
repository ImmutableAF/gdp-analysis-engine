import pytest
import pandas as pd
from dataclasses import dataclass
from src.core.engine import (
    transform,
    _filter_by_region,
    _filter_by_country,
    _filter_by_year,
    aggregate_by_region,
    aggregate_by_country,
    aggregate_by_country_code,
    aggregate_all,
    apply_filters,
    get_query_result,
    run_pipeline,
    EngineError,
)


@dataclass
class MockFilters:
    region: str | None = None
    country: str | None = None
    startYear: int | None = None
    endYear: int | None = None
    operation: str | None = None


def make_wide_df():
    return pd.DataFrame({
        "Country Name":   ["USA", "Germany", "China"],
        "Country Code":   ["US",  "DE",       "CN"],
        "Continent":      ["Americas", "Europe", "Asia"],
        "Indicator Name": ["GDP"] * 3,
        "Indicator Code": ["NY.GDP.MKTP.CD"] * 3,
        "2000": [100.0, 200.0, 300.0],
        "2001": [110.0, 210.0, 310.0],
        "2002": [120.0, 220.0, float("nan")],
    })


def make_long_df():
    return transform(make_wide_df())


class TestTransform:

    def test_returns_long_format(self):
        result = transform(make_wide_df())
        assert "Year" in result.columns
        assert "Value" in result.columns

    def test_year_column_is_int(self):
        result = transform(make_wide_df())
        assert result["Year"].dtype == int

    def test_row_count_is_correct(self):
        result = transform(make_wide_df())
        assert len(result) == 9

    def test_missing_columns_raise_engine_error(self):
        bad_df = pd.DataFrame({"Country Name": ["USA"], "2000": [100.0]})
        with pytest.raises(EngineError):
            transform(bad_df)

    def test_original_df_is_not_modified(self):
        df = make_wide_df()
        _ = transform(df)
        assert "2000" in df.columns


class TestFilterByRegion:

    def test_filters_to_correct_region(self):
        result = _filter_by_region(make_long_df(), "Asia")
        assert all(result["Continent"] == "Asia")

    def test_case_insensitive(self):
        result = _filter_by_region(make_long_df(), "asia")
        assert len(result) > 0

    def test_none_returns_full_copy(self):
        df = make_long_df()
        result = _filter_by_region(df, None)
        assert len(result) == len(df)

    def test_unknown_region_returns_empty(self):
        result = _filter_by_region(make_long_df(), "Atlantis")
        assert len(result) == 0


class TestFilterByCountry:

    def test_filters_to_correct_country(self):
        result = _filter_by_country(make_long_df(), "USA")
        assert all(result["Country Name"] == "USA")

    def test_case_insensitive(self):
        result = _filter_by_country(make_long_df(), "usa")
        assert len(result) > 0

    def test_none_returns_full_copy(self):
        df = make_long_df()
        result = _filter_by_country(df, None)
        assert len(result) == len(df)

    def test_unknown_country_returns_empty(self):
        result = _filter_by_country(make_long_df(), "Wakanda")
        assert len(result) == 0


class TestFilterByYear:

    def test_both_start_and_end_filters_range(self):
        result = _filter_by_year(make_long_df(), start=2000, end=2001)
        assert all(result["Year"].between(2000, 2001))

    def test_only_start_filters_exact_year(self):
        result = _filter_by_year(make_long_df(), start=2000)
        assert all(result["Year"] == 2000)

    def test_only_end_filters_exact_year(self):
        result = _filter_by_year(make_long_df(), end=2001)
        assert all(result["Year"] == 2001)

    def test_none_none_returns_full_copy(self):
        df = make_long_df()
        result = _filter_by_year(df, None, None)
        assert len(result) == len(df)


class TestAggregateByRegion:

    def test_sum_aggregates_by_continent(self):
        result = aggregate_by_region(make_long_df(), "sum")
        assert "Continent" in result.columns
        assert "Value" in result.columns

    def test_mean_aggregates_by_continent(self):
        result = aggregate_by_region(make_long_df(), "mean")
        assert "Continent" in result.columns

    def test_returns_one_row_per_continent(self):
        result = aggregate_by_region(make_long_df(), "sum")
        assert len(result) == 3


class TestAggregateByCountry:
    def test_mean_aggregates_by_country(self):
        result = aggregate_by_country(make_long_df(), "mean")
        assert "Country Name" in result.columns

    def test_sum_aggregates_by_country(self):
        result = aggregate_by_country(make_long_df(), "sum")
        assert "Country Name" in result.columns

    def test_returns_one_row_per_country(self):
        result = aggregate_by_country(make_long_df(), "sum")
        assert len(result) == 3


class TestAggregateByCountryCode:
    def test_mean_aggregates_by_country_code(self):
        result = aggregate_by_country_code(make_long_df(), "mean")
        assert "Country Code" in result.columns

    def test_sum_aggregates_by_country_code(self):
        result = aggregate_by_country_code(make_long_df(), "sum")
        assert "Country Code" in result.columns

    def test_returns_one_row_per_country_code(self):
        result = aggregate_by_country_code(make_long_df(), "sum")
        assert len(result) == 3


class TestAggregateAll:

    def test_sum_adds_operation_column_with_sum(self):
        result = aggregate_all(make_long_df(), "sum")
        assert result["Operation"].iloc[0] == "Sum"

    def test_avg_adds_operation_column_with_average(self):
        result = aggregate_all(make_long_df(), "avg")
        assert result["Operation"].iloc[0] == "Average"

    def test_average_alias_works(self):
        result = aggregate_all(make_long_df(), "average")
        assert result["Operation"].iloc[0] == "Average"

    def test_none_defaults_to_avg(self):
        result = aggregate_all(make_long_df(), None)
        assert result["Operation"].iloc[0] == "Average"

    def test_unknown_operation_returns_df_unchanged(self):
        df = make_long_df()
        result = aggregate_all(df, "unknown_op")
        assert len(result) == len(df)

    def test_case_insensitive_operation(self):
        result = aggregate_all(make_long_df(), "SUM")
        assert result["Operation"].iloc[0] == "Sum"


class TestApplyFilters:

    def test_filters_by_region(self):
        result = apply_filters(make_long_df(), region="Asia")
        assert all(result["Continent"] == "Asia")

    def test_filters_by_country(self):
        result = apply_filters(make_long_df(), country="USA")
        assert all(result["Country Name"] == "USA")

    def test_filters_by_year_range(self):
        result = apply_filters(make_long_df(), start_year=2000, end_year=2001)
        assert all(result["Year"].between(2000, 2001))

    def test_drops_nan_values(self):
        result = apply_filters(make_long_df())
        assert result["Value"].isna().sum() == 0

    def test_all_none_returns_df_without_nans(self):
        df = make_long_df()
        result = apply_filters(df)
        assert len(result) == df["Value"].notna().sum()


class TestRunPipeline:

    def test_returns_dataframe(self):
        filters = MockFilters(operation="sum")
        result = run_pipeline(make_wide_df(), filters)
        assert isinstance(result, pd.DataFrame)

    def test_inlongformat_skips_aggregation(self):
        filters = MockFilters(operation="sum")
        result = run_pipeline(make_wide_df(), filters, inLongFormat=True)
        assert "Operation" not in result.columns

    def test_default_aggregates_result(self):
        filters = MockFilters(operation="sum")
        result = run_pipeline(make_wide_df(), filters)
        assert "Operation" in result.columns

    def test_region_filter_applied(self):
        filters = MockFilters(region="Asia", operation="sum")
        result = run_pipeline(make_wide_df(), filters, inLongFormat=True)
        assert all(result["Continent"] == "Asia")

    def test_no_nan_values_in_output(self):
        filters = MockFilters(operation="sum")
        result = run_pipeline(make_wide_df(), filters, inLongFormat=True)
        assert result["Value"].isna().sum() == 0

class TestGetQueryResult:

    def test_prints_output(self, capsys):
        filters = MockFilters(operation="sum")
        get_query_result(make_wide_df(), filters)
        captured = capsys.readouterr()
        assert len(captured.out) > 0