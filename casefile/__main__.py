import argparse
import os
import prctl
import pty
import sys

from pathlib import Path

from . import __version__
from .config import read_config
from .casefile import new_case, list_cases


def main():
    prctl.set_proctitle("casefile")

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
    parser.add_argument('-s',
                        '--shell',
                        action='store_true',
                        help='Launch a shell in the new casefile directory')

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
        case_path = new_case(args.summary, config['casefile'])
        case = Path(*case_path.parts[-2:])
        prctl.set_proctitle("casefile: {}".format(case))
        if args.shell:
            os.chdir(str(case_path))
            os.putenv("PS1", "{}> ".format(case))
            os.putenv("ZDOTDIR", config['casefile']['base'])
            pty.spawn(['/bin/zsh'])

if __name__ == "__main__":
    main()
