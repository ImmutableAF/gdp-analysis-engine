import pandas as pd
from pathlib import Path
from ..loader_interface import Loader


class ExcelLoader(Loader):
    def supports(self, file_path: Path) -> bool:
        """Checks if the file is an Excel format."""
        return file_path.suffix.lower() in (".xlsx", ".xls")

    def load(self, file_path: Path) -> pd.DataFrame:
        """
        Loads the Excel file and triggers the conversion to CSV.
        """
        df = pd.read_excel(file_path)
        return self.to_csv_dataframe(df, file_path)

    def to_csv_dataframe(self, df: pd.DataFrame, file_path: Path) -> pd.DataFrame:
        """
        Saves the DataFrame as a CSV file with the same name as the original 
        and returns the CSV-formatted data.
        """
        # Generate new path: /path/to/data.xlsx -> /path/to/data.csv
        csv_path = file_path.with_suffix(".csv")
        
        # Export to CSV without the index to keep the data clean for the pipeline
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        # Return the data as a CSV-backed DataFrame
        return pd.read_csv(csv_path)