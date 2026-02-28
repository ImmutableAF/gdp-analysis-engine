import sys
import threading
import time
from pathlib import Path
import uvicorn

sys.path.insert(0, str(Path(__file__).parent))

from plugins.data_loading.loading_manager import load_data
from plugins.config_handler import get_base_config, get_query_config
from core.data_cleaning import clean_gdp_data
from core.api_server import create_server
from plugins.outputs import OutputMode, make_sink
from util.logging_setup import initialize_logging
from util.cli_parser import parse_cli_args

API_PORT = 8010
API_URL = f"http://localhost:{API_PORT}"


def start_api(base_df, default_filters, config_loader, port: int = API_PORT):
    app = create_server(base_df, default_filters, config_loader=config_loader)
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")


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

    api_thread = threading.Thread(
        target=start_api,
        args=(base_df, default_filters, config_loader, API_PORT),
        daemon=True,
    )
    api_thread.start()
    time.sleep(1)

    mode = OutputMode.CLI if getattr(args, "cli", False) else OutputMode.UI
    sink = make_sink(mode, api_url=API_URL)
    sink.start()


if __name__ == "__main__":
    main()