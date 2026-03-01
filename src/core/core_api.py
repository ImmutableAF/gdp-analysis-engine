import orjson
import pandas as pd
from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from dataclasses import dataclass
from typing import Optional, Callable

from .engine import (
    run_pipeline,
    aggregate_by_region,
    aggregate_by_country,
    aggregate_by_country_code,
    aggregate_all,
)
from .metadata import get_metadata
from .contracts import Filters


class FilterBody(BaseModel):
    region: Optional[str] = None
    country: Optional[str] = None
    startYear: Optional[int] = None
    endYear: Optional[int] = None
    operation: Optional[str] = None


@dataclass
class ResolvedFilters:
    region: Optional[str] = None
    country: Optional[str] = None
    startYear: Optional[int] = None
    endYear: Optional[int] = None
    operation: Optional[str] = None


def _to_response(df: pd.DataFrame) -> Response:
    return Response(
        content=orjson.dumps(
            df.to_dict(orient="records"),
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
        ),
        media_type="application/json",
    )


def _resolve(body: Optional[FilterBody], defaults: Filters) -> ResolvedFilters:
    if body is None:
        return ResolvedFilters(
            region=defaults.region,
            country=defaults.country,
            startYear=defaults.startYear,
            endYear=defaults.endYear,
            operation=defaults.operation,
        )
    return ResolvedFilters(
        region=(
            None
            if body.region == "__ALL__"
            else (body.region if body.region is not None else defaults.region)
        ),
        country=body.country if body.country is not None else defaults.country,
        startYear=body.startYear if body.startYear is not None else defaults.startYear,
        endYear=body.endYear if body.endYear is not None else defaults.endYear,
        operation=body.operation if body.operation is not None else defaults.operation,
    )


def _filters_to_dict(f) -> dict:
    return {
        "region": f.region,
        "country": f.country,
        "startYear": f.startYear,
        "endYear": f.endYear,
        "operation": f.operation,
    }


def create_server(
    base_df: pd.DataFrame,
    default_filters: Filters,
    config_loader: Optional[Callable] = None,
) -> FastAPI:
    app = FastAPI(title="GDP Core API")
    meta = get_metadata(base_df)

    @app.get("/metadata")
    def get_meta():
        return meta

    @app.get("/config")
    def get_config():
        return _filters_to_dict(default_filters)

    @app.post("/config/reload")
    def reload_config():
        if config_loader is None:
            raise HTTPException(status_code=501, detail="No config loader registered")
        new_filters = config_loader()
        return _filters_to_dict(new_filters)

    @app.get("/original")
    def get_original():
        return _to_response(base_df)

    @app.post("/run")
    def run(body: Optional[FilterBody] = Body(default=None)):
        filters = _resolve(body, default_filters)
        result = run_pipeline(df=base_df, filters=filters, inLongFormat=True)
        return _to_response(result)

    def _aggregate_helper(pipeline_func, body: Optional[FilterBody] = None):
        filters = _resolve(body, default_filters)
        df = run_pipeline(base_df, filters, inLongFormat=True)
        return pipeline_func(df, filters.operation or "avg")

    @app.post("/aggregate/region")
    def agg_region(body: Optional[FilterBody] = Body(default=None)):
        return _to_response(_aggregate_helper(aggregate_by_region, body))

    @app.post("/aggregate/country")
    def agg_country(body: Optional[FilterBody] = Body(default=None)):
        return _to_response(_aggregate_helper(aggregate_by_country, body))

    @app.post("/aggregate/country-code")
    def agg_country_code(body: Optional[FilterBody] = Body(default=None)):
        return _to_response(_aggregate_helper(aggregate_by_country_code, body))

    @app.post("/aggregate/all")
    def agg_all(body: Optional[FilterBody] = Body(default=None)):
        return _to_response(_aggregate_helper(aggregate_all, body))

    return app
