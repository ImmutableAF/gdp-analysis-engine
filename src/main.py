import sys
import threading
import time
from pathlib import Path
import uvicorn

sys.path.insert(0, str(Path(__file__).parent))

from plugins.data_loading.loading_manager import load_data
from plugins.config_handler import get_base_config, get_query_config
from core.data_cleaning import clean_gdp_data
from src.core.core_api import create_server
from src.plugins.ui.output_api import app as analytics_app
import src.plugins.ui.output_api as analytics_server
from plugins.outputs import OutputMode, make_sink
from util.logging_setup import initialize_logging
from util.cli_parser import parse_cli_args

CORE_PORT = 8010
ANALYTICS_PORT = 8011
CORE_URL = f"http://localhost:{CORE_PORT}"
ANALYTICS_URL = f"http://localhost:{ANALYTICS_PORT}"

def start_core_api(base_df, default_filters, config_loader):
    app = create_server(base_df, default_filters, config_loader=config_loader)
    uvicorn.run(app, host="0.0.0.0", port=CORE_PORT, log_level="warning")


def start_analytics_api():
    uvicorn.run(analytics_app, host="0.0.0.0", port=ANALYTICS_PORT, log_level="warning")


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

    # Start analytics API on :8011 (points at core, test separately)
    analytics_server.CORE_API_URL = CORE_URL
    threading.Thread(target=start_analytics_api, daemon=True).start()

    time.sleep(1)

    # Streamlit sink still uses core API directly as before
    mode = OutputMode.CLI if getattr(args, "cli", False) else OutputMode.UI
    sink = make_sink(mode, api_url=CORE_URL, analytics_url=ANALYTICS_URL)
    sink.start()


if __name__ == "__main__":
    main()