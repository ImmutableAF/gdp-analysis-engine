import subprocess
import sys
import threading
import uvicorn
from pathlib import Path

from src.plugins.outputs import OutputSink
from .api_server import create_app
from src.core.engine import run_pipeline  # your actual filter-aware pipeline call


class UISink(OutputSink):
    def _start_api(self):
        def filter_fn(df, filters):
            return run_pipeline(df=df, filters=filters, inLongFormat=True)

        app = create_app(
            runner=self.runner,
            original_df=self.original_df,
            metadata=self.metadata,
            query_config=self.query_config,
            filter_fn=filter_fn,
        )
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")

    def start(self) -> None:
        api_thread = threading.Thread(target=self._start_api, daemon=True)
        api_thread.start()

        entry = Path(__file__).parent / "streamlit_entry.py"
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(entry)])
