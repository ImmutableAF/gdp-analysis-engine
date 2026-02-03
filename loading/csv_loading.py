from abstract.data_loading import data_loader
import csv
class csvDataLoader(data_loader):
    def load(self, filepath):
        try:
            with open(filepath, 'r', encoding = 'utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            return data
        except FileNotFoundError:
            print(f"Error: {filepath} not found!")
            return []
    def validate(self, data):
        if not data:
            return False
        required_columns = ['Country Name', 'Region', 'Year', 'Value']
        first_row = data[0]
        has_all_cols = all(map(lambda col: col in first_row, required_columns))
        if not has_all_cols:
            missing = list(filter(lambda col: col not in first_row, required_columns))
            print(f"Missing columns: {', '.join(missing)}")
            return False
        return True