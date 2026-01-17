from fetch_news import process_app
import os

if __name__ == "__main__":
    config_file = "config_hailal.json"
    if os.path.exists(config_file):
        print(f"Testing {config_file}...")
        process_app(config_file)
    else:
        print(f"Error: {config_file} not found.")
