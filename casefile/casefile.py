# Copyright (C) 2017-2019 Max R.D. Parmer
# License AGPLv3+: GNU Affero GPL version 3 or later.
# http://www.gnu.org/licenses/agpl.html
'''Provides the core casefile functionality:
    - read cases
    - find cases
    - list cases
    - print case listings
    - creates cases
TODO: capture $USER in case_log() and new_case()
TODO: generalize around log/append operations on notes files
'''

import os

from pathlib import Path
from datetime import timedelta, datetime as dt

from .errors import IncompleteCase, err


def _read_case_notes(notes, full_text=False):
    '''Read the summary notes from a case, optionally reads all the text.'''
    with notes.open() as notes_file:
        summary = notes_file.readline().strip('\n\r# ')
        if full_text:
            details = ''.join(notes_file.readlines()[1:])
            return (summary, details)
        return summary


def find_cases(conf):
    '''Searches the case base and yielding cases as they're found.'''
    base = Path(conf['base'])
    for item in os.listdir(str(base)):
        item = base / item
        if item.is_dir():
            for child in os.listdir(str(item)):
                child = item / str(child)
                if child.is_dir():
                    yield child
                else:
                    continue
                    # TODO: warn users about their directory clutter


def list_cases(conf):
    '''Iterates over found cases yielding a case id and summary as they're
    found.'''
    for case in find_cases(conf):
        notes = case / conf['notes_file']
        case_id = case.relative_to(conf['base'])
        summary = _read_case_notes(notes)
        yield (case_id, summary)


def print_case_listing(conf, grepable=False, sort=False):
    '''Prints listings of found cases.

    If grepable, then each case is renderd on one line.
    If sorted, all cases are discovered and lexically sorted before printing.
    '''
    case_list = list_cases(conf)
    listing_format = '{}:\n\t{}'

    if sort:
        case_list = sorted(case_list)

    if grepable:
        listing_format = '{} {}'

    for case in case_list:
        print(listing_format.format(*case))


def load_case(case_id, conf):
    '''Ensures a case is well-formed enough to use for other purposes.'''
    base = Path(conf['base'])
    expected_notes = base / case_id / conf['notes_file']
    if not expected_notes.exists():
        raise FileNotFoundError(expected_notes)
    return _read_case_notes(expected_notes, full_text=True)


def latest_case(conf, search_limit=100):
    '''Finds the most recently created case.'''
    check_date = dt.today()
    base = Path(conf['base'])
    series = list(conf['case_series'])
    series.reverse()

    attempts = 0
    while True:
        attempts += 1
        date = Path(dt.strftime(check_date, conf['date_fmt']))
        date_dir = base / date
        if date_dir.exists():
            for serial in series:
                case_dir = date_dir / serial
                if case_dir.exists():
                    case = date / serial
                    return case
        else:
            if attempts <= search_limit:
                check_date = check_date - timedelta(days=1)
            else:
                err(f'No new cases in {search_limit} days.', 127)


def case_log(conf, case, note_text):
    '''Logs a timestamped note to an open case.'''
    base = Path(conf['base'])
    case_dir = base / case
    if case_dir.exists():
        notes = case_dir / conf['notes_file']
        if notes.exists():
            timestamp = dt.strftime(dt.today(), '%X')
            with notes.open('a') as notes_file:
                print(f'## {timestamp}: {note_text}', file=notes_file)
    else:
        err(f'The case "{case}" does not exist.', 127)


def new_case(summary, conf, date_override=False):
    '''Allocates a new case ID and creates the appropriate folders.'''
    if not summary:
        try:
            summary = input('Case Summary: ')
        except KeyboardInterrupt:
            summary = input('Please provide a Case Summary: ')

        if not summary:
            raise IncompleteCase()

    base = Path(conf['base'])
    case_directories = conf['case_directories'].split(',')

    # if date_override is set use it's value, otherwise use today's date
    if date_override:
        date = date_override
    else:
        date = dt.strftime(dt.today(), conf['date_fmt'])

    # Initialize the casefile base directory if it doesn't exist
    if not base.exists():
        base.mkdir()
        print(f'Created CaseFile base at {base}')

    # Have we created cases today? If not, create a new date directory.
    date_dir = base / date
    if not date_dir.exists():
        date_dir.mkdir()
        print(f'First case for today, {date}\n')

    # Find the next case in the series
    for serial in conf['case_series']:
        case = date_dir / serial
        if not case.exists():
            case.mkdir()
            for directory in case_directories:
                resource_dir = case / directory
                resource_dir.mkdir()
                if conf.getboolean('verbose'):
                    print(f'Created resource directory {resource_dir}')
            print(f'Case opened:\n\t{case}')
            break
        else:
            continue

    notes = case / conf['notes_file']
    # TODO: make TZ representation configurable (local or UTC)
    # TODO: annotate timestamp with TZ the stamp is in
    timestamp = dt.strftime(dt.today(), '%X')
    with notes.open('a') as notes_file:
        print(f'# {timestamp}:  {summary}', file=notes_file)
