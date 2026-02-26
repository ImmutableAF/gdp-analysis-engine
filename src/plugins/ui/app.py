import subprocess
import sys
from pathlib import Path

from src.plugins.outputs import OutputSink, OutputRunner


class UISink(OutputSink):
    def __init__(self, runner: OutputRunner, metadata: dict) -> None:
        super().__init__(runner, metadata)

    def start(self) -> None:
        entry = Path(__file__).parent / "streamlit_entry.py"
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(entry)])
