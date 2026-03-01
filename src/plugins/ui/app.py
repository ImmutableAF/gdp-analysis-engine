import subprocess
import sys
from pathlib import Path

from src.plugins.outputs import OutputSink, CoreAPIClient


class UISink(OutputSink):
    def __init__(
        self, client: CoreAPIClient, analytics_url: str = "http://localhost:8011"
    ):
        super().__init__(client)
        self._analytics_url = analytics_url

    def start(self) -> None:
        entry = Path(__file__).parent / "streamlit_entry.py"
        import os

        env = {
            **os.environ,
            "CORE_API_URL": self.client._base,
            "ANALYTICS_API_URL": self._analytics_url,
        }
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(entry),
                "--server.address",
                "0.0.0.0",
            ],
            env=env,
        )
