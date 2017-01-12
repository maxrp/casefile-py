import os

from pathlib import Path
from datetime import datetime as dt

def find_cases(base):
    for item in os.scandir(base):
        if item.is_dir():
            yield item

def list_cases(base):
    return [l for l in find_cases(base)]

def new_case(conf, date_override=False):
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
                print("Created resource directory {}".format(resource_dir))
            break
        else:
            continue
