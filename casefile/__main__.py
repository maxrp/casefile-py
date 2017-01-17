import argparse
import sys

from . import __version__
from .config import read_config
from .casefile import new_case, list_cases


def main():
    version = '\n'.join(["%(prog)s (casefile-py) {}",
                         "Copyright (C) 2017 Max R.D. Parmer",
                         "License AGPLv3+: GNU Affero GPL version 3 or later.",
                         "http://www.gnu.org/licenses/agpl.html"])
    parser = argparse.ArgumentParser()
    parser.add_argument('-V',
                        '--version',
                        action='version',
                        version=version.format(__version__))
    parser.add_argument('-l',
                        '--list-cases',
                        action='store_true',
                        )
    subparsers = parser.add_subparsers(help="subcommands")
    new_case_parser = subparsers.add_parser('new', help="New case.")
    new_case_parser.add_argument('summary',
                                 nargs="?",
                                 help="A brief case summary.")
    args = parser.parse_args()
    config = read_config()
    if args.list_cases:
        for case in list_cases(config['casefile']):
            print("{}:\n\t{}".format(*case))
        sys.exit(0)

    if hasattr(args, 'summary'):
        new_case(args.summary, config['casefile'])

if __name__ == "__main__":
    main()
