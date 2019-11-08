# Copyright (C) 2017-2019 Max R.D. Parmer
# License AGPLv3+: GNU Affero GPL version 3 or later.
# http://www.gnu.org/licenses/agpl.html

import argparse
from importlib.util import find_spec
from pathlib import Path

from . import __version__
from .config import find_config, read_config, write_config
from .casefile import new_case, print_case_listing
from .errors import IncompleteCase, err

HAS_REQUESTS = False
if find_spec('requests'):
    HAS_REQUESTS = True
    from urllib.error import HTTPError
    from .jira import jira_post, prep_case

def main():
    version = f'%(prog)s (casefile-py) {__version__}'
    parser = argparse.ArgumentParser()
    parser.add_argument('-V',
                        '--version',
                        action='version',
                        version=version)
    parser.add_argument('-v',
                        '--verbose',
                        action='store_true')
    parser.add_argument('-l',
                        '--list-cases',
                        action='store_true')
    parser.add_argument('-g',
                        '--grepable',
                        action='store_true',
                        help='Output case listings, one per line.')
    parser.add_argument('-s',
                        '--sort',
                        action='store_true',
                        help='Sort cases lexically.')
    parser.add_argument('-c',
                        '--config',
                        help='Default: %(default)s',
                        default=find_config())
    subparsers = parser.add_subparsers(help='subcommands')
    new_case_parser = subparsers.add_parser('new', help='New case.')
    new_case_parser.add_argument('summary',
                                 nargs='?',
                                 help='A brief case summary.')

    if HAS_REQUESTS:
        promote_parser = subparsers.add_parser('promote',
                                               help='Post case notes to Jira.')
        promote_parser.add_argument('case',
                                    nargs='?',
                                    help='Case to post to Jira.')

    args = parser.parse_args()

    config_file = Path(args.config)

    if not config_file.exists():
        try:
            write_config(config_file)
        except KeyboardInterrupt:
            if config_file.exists():
                config_file.unlink()
            err('Configuration of CaseFile cancelled.', 127)
    config = read_config(config_file)

    if args.verbose:
        config['casefile']['verbose'] = 'yes'

    if args.list_cases or args.grepable or args.sort:
        print_case_listing(config['casefile'], args.grepable, args.sort)
    elif hasattr(args, 'summary'):
        try:
            new_case(args.summary, config['casefile'])
        except (KeyboardInterrupt, IncompleteCase):
            err('You must provide a case summary.', 127)
    elif hasattr(args, 'case') and HAS_REQUESTS:
        try:
            summary, details = prep_case(args.case, config['casefile'])
        except FileNotFoundError as missing_file:
            err((f'The case "{args.case}" does not exist or is missing the ',
                 f'expected notes file "{missing_file}"'), 127)

        try:
            jira_post(summary, details, config['casefile'])
        except HTTPError as error:
            err(error, 127)
    else:
        parser.print_usage()


if __name__ == '__main__':
    main()
