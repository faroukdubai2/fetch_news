from gnews import GNews
import json
import os
import sys

OUTPUT_DIR = "docs/data"
CONFIG_FILE = "config.json"


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_json(data, filename: str):
    ensure_output_dir()
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data)} articles to {path}")


def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Config file {CONFIG_FILE} not found!")
        return []
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    config = load_config()
    
    if not config:
        print("No configuration found or empty config file.")
        return

    for entry in config:
        try:
            # Extract basic params
            func_name = entry.get("function")
            filename = entry.get("filename")
            language = entry.get("language", "en")
            country = entry.get("country", "US")
            max_results = entry.get("max_results", 99)
            
            # Additional params (remove known keys to find extras)
            known_keys = {"function", "filename", "language", "country", "max_results"}
            extra_params = {k: v for k, v in entry.items() if k not in known_keys}

            if not func_name or not filename:
                print(f"Skipping invalid entry: {entry}")
                continue

            # Initialize GNews
            gnews = GNews(language=language, country=country, max_results=max_results)

            # Map function names to GNews methods
            data = []
            if func_name == "get_top_news":
                data = gnews.get_top_news()
            elif func_name == "get_news_by_topic":
                topic = extra_params.get("topic")
                if topic:
                    data = gnews.get_news_by_topic(topic)
                else:
                    print(f"Missing 'topic' for {func_name}")
            elif func_name == "get_news": # Keyword search
                keyword = extra_params.get("keyword") or extra_params.get("q")
                if keyword:
                    data = gnews.get_news(keyword)
                else:
                    print(f"Missing 'keyword' for {func_name}")
            elif func_name == "get_news_by_location":
                location = extra_params.get("location")
                if location:
                    data = gnews.get_news_by_location(location)
                else:
                    print(f"Missing 'location' for {func_name}")
            elif func_name == "get_news_by_site":
                site = extra_params.get("site")
                if site:
                    data = gnews.get_news_by_site(site)
                else:
                    print(f"Missing 'site' for {func_name}")
            else:
                print(f"Unknown function: {func_name}")
                continue

            # Save the result
            if data is not None:
                save_json(data, filename)

        except Exception as e:
            print(f"Error processing entry {entry}: {e}")

if __name__ == "__main__":
    main()
