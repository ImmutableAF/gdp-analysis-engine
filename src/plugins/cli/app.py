import sys
from src.plugins.outputs import OutputSink


class CliSink(OutputSink):
    def __init__(self, runner, metadata, original_df=None, query_config=None, config_loader=None) -> None:
        super().__init__(runner, metadata, original_df, query_config, config_loader)

    def _display(self) -> None:
        df = self.runner()
        print(df.to_string())
        print("=" * 96)

    def start(self) -> None:
        self._display()
        print("\n[r] Reload config   [e] Exit\n")

        while True:
            key = input().strip().lower()
            if key == "r":
                print("\nReloading config...\n")
                self.query_config = self._config_loader()
                self._display()
            elif key == "e":
                print("\nExiting safely. Goodbye!")
                sys.exit(0)