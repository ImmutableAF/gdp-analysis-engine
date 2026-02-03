import json
def load_config(filepath = 'config.json'):
    try:
        with open(filepath, 'r') as f:
            config =json.load(f)
            return config
    except FileNotFoundError:
        print(f"Error:  {filepath} not found!")
        return None
    except json.JSONDecodeError:
        print(f"Error: {filepath} is not valid json!")
        return None