import sys
import threading
import time
from pathlib import Path
import httpx
import uvicorn

from src.core import clean_gdp_data, create_server
from src.util import parse_cli_args, initialize_logging
from src.plugins import (
    load_data,
    get_base_config,
    get_query_config,
    make_sink,
    analytics_app,
    analytics_server,
)

CORE_PORT = 8010
ANALYTICS_PORT = 8011
CORE_URL = f"http://localhost:{CORE_PORT}"
ANALYTICS_URL = f"http://localhost:{ANALYTICS_PORT}"


def start_core_api(base_df, default_filters, config_loader):
    app = create_server(base_df, default_filters, config_loader=config_loader)
    uvicorn.run(app, host="0.0.0.0", port=CORE_PORT, log_level="warning")


def start_analytics_api():
    uvicorn.run(analytics_app, host="0.0.0.0", port=ANALYTICS_PORT, log_level="warning")


def _probe(url: str) -> bool:
    """Return True if the URL responds with any non-connection-error status."""
    try:
        httpx.get(url, timeout=2)
        return True  # any HTTP response means the server is up
    except httpx.ConnectError:
        return False  # server not listening yet — keep waiting
    except Exception:
        return True  # got a response (even 4xx/5xx) means server is up


def wait_for_servers(
    probes: dict[str, str], timeout: float = 60.0, interval: float = 0.3
) -> None:
    """
    Block until every probe URL responds.
    probes: { label: url }
    """
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

    # Start core API on :8010
    threading.Thread(
        target=start_core_api,
        args=(base_df, default_filters, config_loader),
        daemon=True,
    ).start()

    # Start analytics API on :8011
    analytics_server.CORE_API_URL = CORE_URL
    threading.Thread(target=start_analytics_api, daemon=True).start()

    # Wait until both servers actually accept connections.
    # Probe /docs — always present on any FastAPI app, no query params needed.
    wait_for_servers(
        {
            "core": f"{CORE_URL}/docs",
            "analytics": f"{ANALYTICS_URL}/docs",
        }
    )

    sink = make_sink(base_config, api_url=CORE_URL, analytics_url=ANALYTICS_URL)
    sink.start()


if __name__ == "__main__":
    main()
