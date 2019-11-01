# Copyright (C) 2017-2019 Max R.D. Parmer
# License AGPLv3+: GNU Affero GPL version 3 or later.
# http://www.gnu.org/licenses/agpl.html

import argparse
from pathlib import Path

from . import __version__
from .config import find_config, read_config, write_config
from .casefile import new_case, list_cases


def main():
    version = "%(prog)s (casefile-py) {}".format(__version__)
    parser = argparse.ArgumentParser()
    parser.add_argument('-V',
                        '--version',
                        action='version',
                        version=version)
    parser.add_argument('-l',
                        '--list-cases',
                        action='store_true',
                        )
    parser.add_argument('-c',
                        '--config',
                        help="Default: %(default)s",
                        default=find_config())
    subparsers = parser.add_subparsers(help="subcommands")
    new_case_parser = subparsers.add_parser('new', help="New case.")
    new_case_parser.add_argument('summary',
                                 nargs="?",
                                 help="A brief case summary.")
    args = parser.parse_args()

    config_file = Path(args.config)

    if not config_file.exists():
        try:
            write_config(config_file)
        except KeyboardInterrupt:
            if config_file.exists():
                config_file.unlink()
            print()
            print('Configuration of CaseFile cancelled.')
            exit(127)

    try:
        config = read_config(config_file)
    except Exception:
        print("Failed to read config.")
        exit(127)

    if args.list_cases:
        for case in list_cases(config['casefile']):
            print("{}:\n\t{}".format(*case))
    elif hasattr(args, "summary"):
        if args.summary:
            new_case(args.summary, config['casefile'])
        else:
            new_case(input("Case Summary: "), config['casefile'])
    else:
        parser.print_usage()


if __name__ == "__main__":
    main()
