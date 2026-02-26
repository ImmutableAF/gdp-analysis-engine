from plugins.outputs import OutputRunner, OutputSink


class CliSink(OutputSink):
    def __init__(self, runner: OutputRunner) -> None:
        super().__init__(runner)

    def start(self) -> None:
        df = self.runner.get("filtered_df")
        print(df.to_string())
        print("=" * 96)
        agg = self.runner.get("region_agg")
        print(agg.to_string())
