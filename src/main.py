import threading
import time
from pathlib import Path
import httpx
import uvicorn

from .core import clean_gdp_data, create_server
from .util import parse_cli_args, initialize_logging
from .plugins import (
    load_data,
    get_base_config,
    get_query_config,
    get_analytics_config,
    get_ports_config,
    make_sink,
    analytics_app,
    analytics_server,
)


def start_core_api(
    base_df, default_filters, config_loader, analytics_config, port: int
):
    app = create_server(
        base_df,
        default_filters,
        config_loader=config_loader,
        analytics_config=analytics_config,
    )
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")


def start_analytics_api(port: int):
    uvicorn.run(analytics_app, host="0.0.0.0", port=port, log_level="warning")


def _probe(url: str) -> bool:
    """Return True if the URL responds with any non-connection-error status."""
    try:
        httpx.get(url, timeout=2)
        return True
    except httpx.ConnectError:
        return False
    except Exception:
        return True


def wait_for_servers(
    probes: dict[str, str], timeout: float = 60.0, interval: float = 0.3
) -> None:
    """Block until every probe URL responds. probes: { label: url }"""
    deadline = time.time() + timeout
    pending = dict(probes)

    while pending:
        if time.time() > deadline:
            raise RuntimeError(
                f"Servers did not start within {timeout}s: {list(pending)}"
            )
        for label, url in list(pending.items()):
            if _probe(url):
                pending.pop(label)
        if pending:
            time.sleep(interval)


def main():
    base_config = get_base_config()
    initialize_logging(base_config, debug=True)

    # Load ports first — needed before any server thread starts.
    ports = get_ports_config()
    core_port = ports.core_port
    analytics_port = ports.analytics_port
    core_url = f"http://localhost:{core_port}"
    analytics_url = f"http://localhost:{analytics_port}"

    args = parse_cli_args()
    filepath = (
        args.file_path
        if (args.file_path and args.file_path.is_file())
        else Path(base_config.data_dir) / base_config.data_filename
    )

    raw_df = load_data(filepath)
    base_df = clean_gdp_data(raw_df)
    default_filters = get_query_config(base_df)
    config_loader = lambda: get_query_config(base_df)

    analytics_config = get_analytics_config(base_df)

    # Start core API
    threading.Thread(
        target=start_core_api,
        args=(base_df, default_filters, config_loader, analytics_config, core_port),
        daemon=True,
    ).start()

    # Start analytics API
    analytics_server.CORE_API_URL = core_url
    threading.Thread(
        target=start_analytics_api,
        args=(analytics_port,),
        daemon=True,
    ).start()

    wait_for_servers(
        {
            "core": f"{core_url}/docs",
            "analytics": f"{analytics_url}/docs",
        }
    )

    sink = make_sink(base_config, api_url=core_url, analytics_url=analytics_url)
    sink.start()


if __name__ == "__main__":
    main()
