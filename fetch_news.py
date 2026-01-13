from gnews import GNews
import json
import os
import sys
import urllib.parse

OUTPUT_DIR = "docs/data"
CONFIG_FILE = "config.json"


def ensure_output_dir(path):
    os.makedirs(path, exist_ok=True)


def transform_filename(filename):
    """
    Transform filename from format like 'usa_top_news.json' to 'top.json'
    Removes 'usa_' prefix and '_news' suffix
    """
    # Remove .json extension
    name = filename.replace('.json', '')

    # Remove usa_ prefix
    if name.startswith('usa_'):
        name = name[4:]

    # Remove _news suffix
    if name.endswith('_news'):
        name = name[:-5]

    return f"{name}.json"


def save_json(data, app_folder, filename: str):
    """Save JSON data to the app folder"""
    ensure_output_dir(app_folder)
    path = os.path.join(app_folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data)} articles to {path}")


def generate_config_json(app_name, repository, app_folder, filenames):
    """
    Generate config.json with all raw GitHub URLs
    """
    # Extract repo path from repository URL
    repo_path = repository.replace('https://github.com/', '').replace('.git', '')

    # URL encode the app name for the path
    encoded_app_name = urllib.parse.quote(app_name)

    # Build raw URLs for each file
    raw_urls = {}
    for filename in sorted(filenames):
        # Remove .json extension for the key
        key = filename.replace('.json', '')
        # Construct raw GitHub URL
        raw_url = f"https://raw.githubusercontent.com/{repo_path}/main/docs/data/{encoded_app_name}/{filename}"
        raw_urls[key] = raw_url

    # Create config structure
    config = {
        "app_name": app_name,
        "repository": repository,
        "raw_urls": raw_urls
    }

    # Save config.json in the app folder
    config_path = os.path.join(app_folder, "config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"Generated config.json with {len(raw_urls)} URLs at {config_path}")


def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Config file {CONFIG_FILE} not found!")
        return None
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    config = load_config()

    if not config:
        print("No configuration found or empty config file.")
        return

    # Extract app metadata
    app_name = config.get("app_name", "Unknown App")
    repository = config.get("repository", "")
    news_sources = config.get("news_sources", [])

    if not news_sources:
        print("No news sources found in config.")
        return

    # Create app-specific folder
    app_folder = os.path.join(OUTPUT_DIR, app_name)
    ensure_output_dir(app_folder)
    print(f"Created app folder: {app_folder}")

    # Track all generated filenames for config.json
    generated_files = []

    for entry in news_sources:
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

            # Transform filename to new format
            new_filename = transform_filename(filename)

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
            elif func_name == "get_news":  # Keyword search
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

            # Save the result with transformed filename
            if data is not None:
                save_json(data, app_folder, new_filename)
                generated_files.append(new_filename)

        except Exception as e:
            print(f"Error processing entry {entry}: {e}")

    # Generate config.json with raw URLs
    if generated_files and repository:
        generate_config_json(app_name, repository, app_folder, generated_files)
    else:
        print("Skipping config.json generation (no files or repository URL)")

    print(f"\nCompleted! Generated {len(generated_files)} files in {app_folder}")


if __name__ == "__main__":
    main()
