import json
import os

CONFIG_PATH = os.path.expanduser("~/Documents/writerdeck/config.json")

def load_config():
    """Loads the configuration from the JSON file."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_config(data):
    """Saves the given data to the JSON configuration file."""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error saving config file: {e}")
