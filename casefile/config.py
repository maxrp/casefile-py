# Copyright (C) 2017-2021 Max R.D. Parmer
# License AGPLv3+: GNU Affero GPL version 3 or later.
# http://www.gnu.org/licenses/agpl.html

"""cf has a configuration file named casefile.ini or .casefile.ini

This module defines all the functions for finding, reading, and writing
casefile.ini
"""

from configparser import ConfigParser
from functools import partial
from os import getenv
from pathlib import Path
from string import ascii_uppercase
from sys import platform
from typing import Any

from .errors import UnsupportedPlatform

# TODO: cast paths (base) to Path at parsing
# TODO: cast lists (case_series, case_directories) to list at parsing
# Refine ConfigParser to CasefileConfigParser, an alias with interpolation disabled
CasefileConfigParser = partial(ConfigParser, interpolation=None)


def find_config(config_name: str = "casefile.ini") -> Path:
    """Find the most likely casefile.ini location in a platform
    convention-aware fashion.

    The first stop is XDG_CONFIG_HOME, followed by ~/.config, followed by
    ~/.casefile.ini, and after that we go to the macOS filesystem hierarchy
    specified location.
    """
    if platform.startswith("darwin"):
        cfg = (
            Path.home()
            / "Library"
            / "Application Support"
            / "is.trystero.CaseFile"
            / config_name
        )
    elif platform.startswith("linux") or ("bsd" in platform):
        xdg_cfg_home = getenv("XDG_CONFIG_HOME")
        dot_config = Path.home() / ".config"

        if xdg_cfg_home:
            cfg = Path(xdg_cfg_home) / config_name
        elif dot_config.exists():
            cfg = dot_config / config_name
        else:
            cfg = Path.home() / f".{config_name}"
    else:
        raise UnsupportedPlatform(f"{platform} support is not implemented.")

    return cfg


def _input_or_default(prompt: str, default: Any) -> Any:
    """A wrapper around input() which has a predefined default.

    prompt is the text to display to the user
    default is the value to return if the user just hits enter
    """
    userval: Any = input(f"{prompt}? [{default}]: ")
    if userval:
        if userval.lower() in ["y", "yes", "si", "sure"]:
            userval = True
        elif userval.lower in ["n", "no"]:
            userval = False
        return userval
    return default


def write_config(config_file: Path) -> Path:
    """A wizard to aid in creating a casefile.ini when one does not yet exist.

    config_file is the destination to write out to.
    """
    init = f'Would you like to create the configuration file "{config_file}"'
    if not _input_or_default(init, "Yes"):
        raise Exception(f'User aborted creation of config "{config_file}"')

    if not config_file.parent.exists():
        config_file.parent.mkdir()

    with config_file.open("w") as new_config_file:
        config = CasefileConfigParser()
        config["casefile"] = {
            "base": _input_or_default("CaseFile Base", Path.home() / "cases"),
            "case_directories": _input_or_default("Case Directories", "raw,processed"),
            "case_series": _input_or_default("Case Serial Series", ascii_uppercase),
            "date_fmt": _input_or_default("Date Format", "%Y-%m-%d"),
            "notes_file": _input_or_default("Notes File", "notes.md"),
        }
        if _input_or_default("Configure Jira?", "No"):
            jira = {
                "jira_user": input("Jira user (user@domain): "),
                "jira_key": input("Jira REST API key: "),
                "jira_proj": input("Jira project to post cases in: "),
                "jira_type": input("Jira issue type: "),
                "jira_domain": input("Jira domain (e.g. evilcorp.atlassian.net): "),
            }
            config["casefile"].update(jira)
        config.write(new_config_file)

    print(f"Created CaseFile configuration in {config_file}")
    return config_file


def read_config(config_file: Path) -> ConfigParser:
    """Try to read the configuration file, returning the parsed config."""
    config = CasefileConfigParser()
    with config_file.open("r") as cfg:
        config.read_file(cfg)

    return config
