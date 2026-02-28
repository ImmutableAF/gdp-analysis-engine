import subprocess
import sys
from pathlib import Path

from src.plugins.outputs import OutputSink, CoreAPIClient


class UISink(OutputSink):
    """
    Launches Streamlit. The streamlit app talks directly to the
    core API server via CoreAPIClient — no local data held here.
    """

    def __init__(self, client: CoreAPIClient):
        super().__init__(client)

    def start(self) -> None:
        entry = Path(__file__).parent / "streamlit_entry.py"
        # Pass the API base URL to Streamlit via env var so it can build its own client
        import os
        env = {**os.environ, "CORE_API_URL": self.client._base}
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(entry)],
            env=env,
        )