"""
A file that stores all the variables that much be read from the env file. Helps me keep track of them at one place, instead of reading and using them where they are needed. This application relies on env for config.

Config is store in a JSON file. TOML, YAML, and ini were options but

TOML - built in library can't write. Don't want to package another module.
YAML - Built in and ugly
.ini - Ugly

"""

from json import JSONDecodeError
from json import dump as json_dump
from json import load as json_load
from os import getenv
from pathlib import Path
from sys import platform
from typing import Literal, NotRequired, TypedDict


class Config(TypedDict):
    ignored_users: list[str]
    no_of_posts_to_print: int
    ignore_all_mod_posts: bool
    default_subreddit: NotRequired[str]


default_config: Config = {
    "ignored_users": ["2soccer2bot", "AutoModerator"],
    "no_of_posts_to_print": 10,
    "ignore_all_mod_posts": True,
}

config_folder: Path

if platform == "win32":
    config_folder = Path(getenv("LOCALAPPDATA", "./config/"))
elif platform == "darwin":
    config_folder = Path("~/Library/Application Support/")
elif platform == "linux":
    config_folder = Path("~/.config/")
else:
    config_folder = Path("./config/")

config_folder = config_folder / "creddit"
config_folder.mkdir(parents=True, exist_ok=True)

# It's actually a cursed thing that you can divide paths.
config_path: Path = config_folder / "config.json"
"""The path of the config"""


def check_config_existence() -> bool:
    """Checks if a config file exists, and that it valid

    Returns:
        bool: True if file exists and contains all required keys
    """
    if not Path(config_path).exists():
        return False

    with open(config_path, "r") as f:
        try:
            config = json_load(f)
        except JSONDecodeError:
            return False
        if not (config or (default_config.keys() < config.keys())):
            return False

    return True


def read_config(config_path: Path = config_path) -> Config:
    """Read the config file"""

    with open(config_path, "r") as f:
        config: Config = json_load(f)

    required_keys = default_config.keys()

    if required_keys <= config.keys():
        # Looks like all keys are present
        return config

    raise RuntimeError("Looks like some values in the config file are missing")


def create_config(c: dict | Config = default_config) -> bool:
    required_keys = default_config.keys()

    if required_keys <= c.keys():
        # All the must have keys are present
        with open(config_path, "w+") as f:
            json_dump(c, f, indent=4, sort_keys=True)
            return True

    return False


def edit_config(new_config: dict) -> bool:
    c = read_config()
    key: Literal[
        "ignored_users",
        "no_of_posts_to_print",
        "ignore_all_mod_posts",
        "default_subreddit",
    ]
    for key in new_config:
        c[key] = new_config[key]
    with open(config_path, "w") as f:
        json_dump(c, f, indent=4, sort_keys=True)
        return True
    return False
