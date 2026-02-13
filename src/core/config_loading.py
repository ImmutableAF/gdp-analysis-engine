import json
import os
from pathlib import Path

config_file_path = os.path.join(os.path.dirname(__file__), 'config.json')
config_path = Path(config_file_path)

def get_config():
    if not config_path.exists():
        raise FileNotFoundError(f"The config file '{config_file_path}' was not found.")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Failed to decode JSON from '{config_file_path}': {e.msg}", e.doc, e.pos)

    return config_data