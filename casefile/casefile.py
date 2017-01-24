import os

from pathlib import Path
from datetime import datetime as dt

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
        with notes.open() as notes_file:
            summary = notes_file.readline().strip('\n\r# ')
        yield (case_id, summary)

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
        print("Created Casefile base at {}.".format(base))

    # Have we created cases today? If not, create a new date directory.
    date_dir = base / date
    if not date_dir.exists():
        date_dir.mkdir()
        print("Created directory for cases initiated {}.".format(date))

    # Find the next case in the series
    for serial in conf['case_series']:
        case = date_dir / serial
        if not case.exists():
            case.mkdir()
            print("Created case {}.".format(case))
            for directory in case_directories:
                resource_dir = case / directory
                resource_dir.mkdir()
                print("Created resource directory {}".format(resource_dir))
            break
        else:
            continue

    notes = case / conf['notes_file']
    timestamp = dt.strftime(dt.today(), "%X")
    with notes.open('a') as notes_file:
        print("# {}:  {}".format(timestamp, summary), file=notes_file)
