# Copyright (C) 2017-2019 Max R.D. Parmer
# License AGPLv3+: GNU Affero GPL version 3 or later.
# http://www.gnu.org/licenses/agpl.html

import os

from pathlib import Path
from datetime import datetime as dt


def _read_case_notes(notes, full_text=False):
    with notes.open() as notes_file:
        summary = notes_file.readline().strip('\n\r# ')
        if full_text:
            details = "".join(notes_file.readlines()[1:])
            return (summary, details)
        else:
            return summary


def find_cases(conf):
    base = Path(conf['base'])
    for item in os.listdir(str(base)):
        item = base / item
        if item.is_dir():
            for child in os.listdir(str(item)):
                child = item / str(child)
                yield child


def list_cases(conf):
    for case in find_cases(conf):
        notes = case / conf['notes_file']
        case_id = case.relative_to(conf['base'])
        summary = _read_case_notes(notes)
        yield (case_id, summary)


def load_case(case_id, conf):
    base = Path(conf['base'])
    expected_notes = base / case_id / conf['notes_file']
    if expected_notes.exists():
        return _read_case_notes(expected_notes, full_text=True)
    else:
        raise FileNotFoundError(expected_notes)

def new_case(summary, conf, date_override=False):
    base = Path(conf['base'])
    case_directories = conf['case_directories'].split(",")

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
    timestamp = dt.strftime(dt.today(), "%X")
    with notes.open('a') as notes_file:
        print("# {}:  {}".format(timestamp, summary), file=notes_file)
