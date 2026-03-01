import pytest
import pandas as pd
from dataclasses import dataclass
from typing import Optional
from unittest.mock import patch
from fastapi.testclient import TestClient

from ..core_api import create_server, _to_response, _resolve, _filters_to_dict, FilterBody, ResolvedFilters


# ── Helpers ───────────────────────────────────────────────────────────────────

@dataclass
class FakeFilters:
    region: Optional[str] = "Europe"
    country: Optional[str] = "Germany"
    startYear: Optional[int] = 1990
    endYear: Optional[int] = 2020
    operation: Optional[str] = "avg"


def make_base_df():
    return pd.DataFrame({
        "Country Name": ["Germany", "France"],
        "Continent":    ["Europe", "Europe"],
        "Year":         [2000, 2000],
        "Value":        [1000.0, 2000.0],
    })


def make_client(df=None, filters=None, config_loader=None):
    df = df if df is not None else make_base_df()
    filters = filters if filters is not None else FakeFilters()
    app = create_server(df, filters, config_loader)
    return TestClient(app)


# ── ToResponse ────────────────────────────────────────────────────────────────

class TestToResponse:

    def test_returns_json_response(self):
        df = make_base_df()
        response = _to_response(df)
        assert response.media_type == "application/json"

    def test_response_body_is_list_of_records(self):
        import orjson
        df = make_base_df()
        response = _to_response(df)
        data = orjson.loads(response.body)
        assert isinstance(data, list)
        assert len(data) == 2

    def test_empty_dataframe_returns_empty_list(self):
        import orjson
        df = pd.DataFrame()
        response = _to_response(df)
        data = orjson.loads(response.body)
        assert data == []


# ── Resolve ───────────────────────────────────────────────────────────────────

class TestResolve:

    def test_none_body_uses_defaults(self):
        defaults = FakeFilters()
        result = _resolve(None, defaults)
        assert result.region == "Europe"
        assert result.country == "Germany"
        assert result.startYear == 1990
        assert result.endYear == 2020
        assert result.operation == "avg"

    def test_body_fields_override_defaults(self):
        defaults = FakeFilters()
        body = FilterBody(region="Asia", country="Japan", startYear=2000, endYear=2010, operation="sum")
        result = _resolve(body, defaults)
        assert result.region == "Asia"
        assert result.country == "Japan"
        assert result.startYear == 2000
        assert result.endYear == 2010
        assert result.operation == "sum"

    def test_none_body_fields_fall_back_to_defaults(self):
        defaults = FakeFilters()
        body = FilterBody(region=None, country=None)
        result = _resolve(body, defaults)
        assert result.region == "Europe"
        assert result.country == "Germany"

    def test_all_sentinel_resets_region_to_none(self):
        defaults = FakeFilters(region="Europe")
        body = FilterBody(region="__ALL__")
        result = _resolve(body, defaults)
        assert result.region is None

    def test_returns_resolved_filters_instance(self):
        result = _resolve(None, FakeFilters())
        assert isinstance(result, ResolvedFilters)


# ── FiltersToDIct ─────────────────────────────────────────────────────────────

class TestFiltersToDIct:

    def test_returns_dict(self):
        result = _filters_to_dict(FakeFilters())
        assert isinstance(result, dict)

    def test_contains_all_keys(self):
        result = _filters_to_dict(FakeFilters())
        assert set(result.keys()) == {"region", "country", "startYear", "endYear", "operation"}

    def test_values_match_filter_fields(self):
        result = _filters_to_dict(FakeFilters())
        assert result["region"] == "Europe"
        assert result["country"] == "Germany"
        assert result["startYear"] == 1990
        assert result["endYear"] == 2020
        assert result["operation"] == "avg"

    def test_none_values_are_preserved(self):
        result = _filters_to_dict(FakeFilters(region=None, country=None))
        assert result["region"] is None
        assert result["country"] is None


# ── GET /metadata ─────────────────────────────────────────────────────────────

class TestGetMetadata:

    def test_returns_200(self):
        client = make_client()
        response = client.get("/metadata")
        assert response.status_code == 200

    def test_response_contains_expected_keys(self):
        client = make_client()
        response = client.get("/metadata")
        data = response.json()
        assert "regions" in data
        assert "countries" in data
        assert "year_range" in data


# ── GET /config ───────────────────────────────────────────────────────────────

class TestGetConfig:

    def test_returns_200(self):
        client = make_client()
        response = client.get("/config")
        assert response.status_code == 200

    def test_returns_all_filter_keys(self):
        client = make_client()
        response = client.get("/config")
        data = response.json()
        assert set(data.keys()) == {"region", "country", "startYear", "endYear", "operation"}

    def test_returns_correct_default_values(self):
        client = make_client(filters=FakeFilters(region="Asia", operation="sum"))
        response = client.get("/config")
        data = response.json()
        assert data["region"] == "Asia"
        assert data["operation"] == "sum"


# ── POST /config/reload ───────────────────────────────────────────────────────

class TestReloadConfig:

    def test_returns_501_when_no_config_loader(self):
        client = make_client(config_loader=None)
        response = client.post("/config/reload")
        assert response.status_code == 501

    def test_returns_200_when_config_loader_provided(self):
        new_filters = FakeFilters(region="Asia")
        client = make_client(config_loader=lambda: new_filters)
        response = client.post("/config/reload")
        assert response.status_code == 200

    def test_returns_new_filters_from_loader(self):
        new_filters = FakeFilters(region="Asia", operation="sum")
        client = make_client(config_loader=lambda: new_filters)
        response = client.post("/config/reload")
        data = response.json()
        assert data["region"] == "Asia"
        assert data["operation"] == "sum"


# ── GET /original ─────────────────────────────────────────────────────────────

class TestGetOriginal:

    def test_returns_200(self):
        client = make_client()
        response = client.get("/original")
        assert response.status_code == 200

    def test_returns_list_of_records(self):
        client = make_client()
        response = client.get("/original")
        data = response.json()
        assert isinstance(data, list)

    def test_returns_correct_row_count(self):
        client = make_client()
        response = client.get("/original")
        data = response.json()
        assert len(data) == 2


# ── POST /run ─────────────────────────────────────────────────────────────────

class TestPostRun:

    def test_returns_200(self):
        client = make_client()
        with patch("src.core.core_api.run_pipeline", return_value=make_base_df()):
            response = client.post("/run")
        assert response.status_code == 200

    def test_returns_list_of_records(self):
        client = make_client()
        with patch("src.core.core_api.run_pipeline", return_value=make_base_df()):
            response = client.post("/run")
        assert isinstance(response.json(), list)

    def test_accepts_filter_body(self):
        client = make_client()
        with patch("src.core.core_api.run_pipeline", return_value=make_base_df()):
            response = client.post("/run", json={"region": "Europe", "operation": "sum"})
        assert response.status_code == 200


# ── POST /aggregate/region ────────────────────────────────────────────────────

class TestAggregateRegion:

    def test_returns_200(self):
        client = make_client()
        fake_agg = pd.DataFrame({"Continent": ["Europe"], "Value": [1500.0]})
        with patch("src.core.core_api.run_pipeline", return_value=make_base_df()), \
             patch("src.core.core_api.aggregate_by_region", return_value=fake_agg):
            response = client.post("/aggregate/region")
        assert response.status_code == 200

    def test_returns_list(self):
        client = make_client()
        fake_agg = pd.DataFrame({"Continent": ["Europe"], "Value": [1500.0]})
        with patch("src.core.core_api.run_pipeline", return_value=make_base_df()), \
             patch("src.core.core_api.aggregate_by_region", return_value=fake_agg):
            response = client.post("/aggregate/region")
        assert isinstance(response.json(), list)


# ── POST /aggregate/country ───────────────────────────────────────────────────

class TestAggregateCountry:

    def test_returns_200(self):
        client = make_client()
        fake_agg = pd.DataFrame({"Country Name": ["Germany"], "Value": [1000.0]})
        with patch("src.core.core_api.run_pipeline", return_value=make_base_df()), \
             patch("src.core.core_api.aggregate_by_country", return_value=fake_agg):
            response = client.post("/aggregate/country")
        assert response.status_code == 200


# ── POST /aggregate/country-code ─────────────────────────────────────────────

class TestAggregateCountryCode:

    def test_returns_200(self):
        client = make_client()
        fake_agg = pd.DataFrame({"Country Code": ["DEU"], "Value": [1000.0]})
        with patch("src.core.core_api.run_pipeline", return_value=make_base_df()), \
             patch("src.core.core_api.aggregate_by_country_code", return_value=fake_agg):
            response = client.post("/aggregate/country-code")
        assert response.status_code == 200


# ── POST /aggregate/all ───────────────────────────────────────────────────────

class TestAggregateAll:

    def test_returns_200(self):
        client = make_client()
        fake_agg = pd.DataFrame({"Value": [1250.0]})
        with patch("src.core.core_api.run_pipeline", return_value=make_base_df()), \
             patch("src.core.core_api.aggregate_all", return_value=fake_agg):
            response = client.post("/aggregate/all")
        assert response.status_code == 200