#!/usr/bin/env python3
import json
import logging
import re
import socket
import sys
import urllib.request
from logging.handlers import SysLogHandler
from pathlib import Path

syslog_handler = SysLogHandler(address="/dev/log", facility=SysLogHandler.LOG_AUTH)

logging.basicConfig(
    level=logging.INFO,
    format=f"{__file__}: %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stderr), syslog_handler],
)


def fetch_json_content(username: str) -> str | None:
    url = f"https://raw.githubusercontent.com/sfg-autonomous-systems/sfg_ssh_setup/main/keys/{username}/authorized_keys.json"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.read().decode("utf-8")
    except Exception as error:
        logging.error(
            f"Failed to fetch authorized keys JSON for user '{username}' using {url}: {error}"
        )
        return None


def get_authorized_keys(username: str, json_content: str | None) -> list | None:
    cache_dir = Path(__file__).parent.parent / "keys" / username
    json_cache_filepath = cache_dir / "authorized_keys.json"

    if json_content is not None:
        json_cache_filepath.parent.mkdir(parents=True, exist_ok=True)
        json_cache_filepath.write_text(json_content)

    if not json_cache_filepath.exists():
        return None

    try:
        with open(json_cache_filepath) as file:
            json_file = json.loads(file.read())
    except json.JSONDecodeError as error:
        logging.error(
            f"Failed to parse cached authorized keys JSON for user '{username}': {error}"
        )
        return None

    authorized_keys = []
    hostname = socket.gethostname()

    for user in json_file.get("users", []):
        if re.fullmatch(user["authorized_for"], hostname) is None:
            continue

        name = user["name"]
        key_cache_filepath = cache_dir / f"{name}.keys"

        try:
            with urllib.request.urlopen(
                f"https://github.com/{name}.keys", timeout=10
            ) as response:
                keys = response.read().decode("utf-8").strip().splitlines()
                authorized_keys.extend(keys)
                key_cache_filepath.write_text("\n".join(keys))

        except Exception as error:
            logging.error(f"Failed to fetch keys from GitHub for '{name}': {error}")

            if key_cache_filepath.exists():
                logging.info(f"Using cached keys for '{name}'.")
                authorized_keys.extend(key_cache_filepath.read_text().splitlines())

    return authorized_keys


def main(username: str) -> None:
    json_content = fetch_json_content(username)
    authorized_keys = get_authorized_keys(username, json_content)

    if authorized_keys is not None:
        print("\n".join(authorized_keys))
    else:
        print("")


if __name__ == "__main__":
    main(sys.argv[1])
