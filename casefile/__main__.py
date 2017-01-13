import argparse

from . import __version__
from .config import read_config
from .casefile import new_case


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
    parser.add_argument('summary',
                        nargs="?",
                        help="A brief case summary.")
    args = parser.parse_args()
    config = read_config()
    new_case(args.summary, config['casefile'])

if __name__ == "__main__":
    main()
