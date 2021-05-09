# Copyright (C) 2017-2021 Max R.D. Parmer
# License AGPLv3+: GNU Affero GPL version 3 or later.
# http://www.gnu.org/licenses/agpl.html

"""main() for the cf utility."""

import argparse
from importlib.util import find_spec
from pathlib import Path

from . import __version__
from .config import find_config, read_config, write_config
from .casefile import CaseFile
from .errors import IncompleteCase, err

HAS_REQUESTS = False
if find_spec("requests"):
    HAS_REQUESTS = True
    from urllib.error import HTTPError
    from .jira import jira_post, prep_case


def main():
    """Serves as the `cf` entry point.

    Handles arguments and performs top-level error handling."""

    version = f"%(prog)s v{__version__}"
    parser = argparse.ArgumentParser()
    parser.add_argument("-V", "--version", action="version", version=version)
    parser.add_argument("-l", "--list-cases", action="store_true")
    parser.add_argument(
        "-g",
        "--grepable",
        action="store_true",
        help="Output case listings, one per line.",
    )
    parser.add_argument(
        "-s", "--sort", action="store_true", help="Sort cases lexically."
    )
    parser.add_argument(
        "-c", "--config", help="Default: %(default)s", default=find_config()
    )
    subparsers = parser.add_subparsers(help="subcommands", dest="cmd")
    new_case_parser = subparsers.add_parser("new", help="New case.")
    new_case_parser.add_argument("summary", nargs="?", help="A brief case summary.")

    log_parser = subparsers.add_parser("log", help="Add a log entry to a case.")
    log_parser.add_argument("case", nargs=2, help="The case to log to and a note.")

    log_quick_parser = subparsers.add_parser(
        "log-quick", help="Add a log entry to a case."
    )
    log_quick_parser.add_argument(
        "note", nargs="?", help="Add a note to the latest case."
    )

    if HAS_REQUESTS:
        promote_parser = subparsers.add_parser(
            "promote", help="Post case notes to Jira."
        )
        promote_parser.add_argument("case", nargs="?", help="Case to post to Jira.")

    args = parser.parse_args()

    config_file = Path(args.config)

    if not config_file.exists():
        try:
            write_config(config_file)
        except KeyboardInterrupt:
            if config_file.exists():
                config_file.unlink()
            err("Configuration of CaseFile cancelled.", 127)
    config = read_config(config_file)["casefile"]

    casefile = CaseFile(config)

    if args.list_cases or args.grepable or args.sort:
        casefile.print_listing(args.grepable, args.sort)
    elif args.cmd == "new":
        try:
            # TODO: wire up date_override to the CLI
            casefile.new(args.summary)
        except (KeyboardInterrupt, IncompleteCase):
            err("You must provide a case summary.", 127)
    elif args.cmd == "promote" and HAS_REQUESTS:
        try:
            summary, details = prep_case(config["casefile"], args.case)
        except FileNotFoundError as missing_file:
            err(
                (
                    f'The case "{args.case}" does not exist or is missing the ',
                    f'expected notes file "{missing_file}"',
                ),
                127,
            )

        try:
            jira_post(config["casefile"], summary, details)
        except HTTPError as error:
            err(error, 127)
    elif args.cmd == "log":
        case = args.case[0]
        note = args.case[1]
        casefile.log(case, note)
    elif args.cmd == "log-quick":
        case = casefile.latest()
        casefile.log(case, args.note)
    else:
        parser.print_usage()


if __name__ == "__main__":
    main()
