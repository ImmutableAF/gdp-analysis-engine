import orjson
import pandas as pd
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from dataclasses import dataclass
from typing import Dict, Any, Callable

from src.plugins.outputs import OutputRunner


@dataclass
class FilterParams:
    region: str | None = None
    country: str | None = None
    startYear: int | None = None
    endYear: int | None = None
    operation: str | None = None


class FilterRequest(BaseModel):
    filters: Dict[str, Any]


def df_to_response(df: pd.DataFrame) -> Response:
    return Response(
        content=orjson.dumps(
            df.to_dict(orient="records"),
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
        ),
        media_type="application/json",
    )


def create_app(
    runner: OutputRunner,
    original_df: pd.DataFrame,
    metadata: dict,
    query_config,
    filter_fn: Callable[[pd.DataFrame, Any], pd.DataFrame],
) -> FastAPI:

    app = FastAPI()

    @app.get("/config")
    def get_config():
        return {
            "region": query_config.region,
            "country": query_config.country,
            "startYear": query_config.startYear,
            "endYear": query_config.endYear,
            "operation": query_config.operation,
        }

    @app.get("/original")
    def get_original():
        return df_to_response(original_df)

    @app.get("/metadata")
    def get_meta():
        return metadata

    @app.post("/run")
    def run_with_filters(req: FilterRequest):
        try:
            query_config = FilterParams(**req.filters)
            result_df = filter_fn(original_df, query_config)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        return df_to_response(result_df)

    @app.get("/run/{endpoint_name}")
    def run_endpoint(endpoint_name: str):
        try:
            result = runner.get(endpoint_name)
            if isinstance(result, pd.DataFrame):
                return df_to_response(result)
            return result
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e))

    return app
