# Copyright (C) 2017-2021 Max R.D. Parmer
# License AGPLv3+: GNU Affero GPL version 3 or later.
# http://www.gnu.org/licenses/agpl.html
"""Provides the core casefile functionality:
    - read cases
    - find cases
    - list cases
    - print case listings
    - creates cases
"""

import os

from datetime import timedelta, datetime as dt
from pathlib import Path
from typing import Iterable, Iterator, Mapping, Tuple

from .errors import IncompleteCase, err


def _read_case_notes(notes: Path) -> str:
    """Read the summary notes from a case, optionally reads all the text."""
    with notes.open() as notes_file:
        summary = notes_file.readline().strip("\n\r# ")
        return summary


def _read_case_body(notes: Path) -> str:
    """Read the summary notes from a case, optionally reads all the text."""
    with notes.open() as notes_file:
        body = "".join(notes_file.readlines()[1:])
        return body


class CaseFile:
    def __init__(self, conf: Mapping[str, str]):
        self.base = Path(conf["base"])
        self.series = list(conf["case_series"])
        self.directories = conf["case_directories"].split(",")
        self.notes = conf["notes_file"]
        self.date_fmt = conf["date_fmt"]

    def find_cases(self) -> Iterator[Path]:
        """Searches the case base and yielding cases as they're found."""
        for listing_item in os.listdir(str(self.base)):
            item = self.base / listing_item
            if item.is_dir():
                for listing_child in os.listdir(str(item)):
                    child = item / listing_child
                    if child.is_dir():
                        yield child
                    else:
                        continue
                        # TODO: warn users about their directory clutter

    def list_cases(self) -> Iterator[Tuple[Path, str]]:
        """Iterates over found cases yielding a case id and summary as they're
        found."""
        for case in self.find_cases():
            notes = case / self.notes
            case_id = case.relative_to(self.base)
            summary = _read_case_notes(notes)
            yield (case_id, summary)

    def print_listing(self, grepable: bool = False, sort: bool = False) -> None:
        """Prints listings of found cases.

        If grepable, then each case is rendered on one line.
        If sort, all cases are discovered and lexically sorted before printing.
        """
        case_list: Iterable[Tuple[Path, str]] = self.list_cases()
        listing_format = "{}:\n\t{}"

        if sort:
            case_list = sorted(case_list)

        if grepable:
            listing_format = "{} {}"

        for case in case_list:
            print(listing_format.format(*case))

    def load_case(self, case_id: str) -> Tuple[str, str]:
        """Ensures a case exists, then loads it."""
        expected_notes = self.base / case_id / self.notes
        if not expected_notes.exists():
            raise FileNotFoundError(expected_notes)
        return (_read_case_notes(expected_notes), _read_case_body(expected_notes))

    def latest(self, search_limit: int = 100) -> Path:
        """Finds the most recently created case."""
        check_date = dt.today()
        series = self.series  # NOTE: unnecessary? check later
        series.reverse()

        attempts = 0
        while True:
            attempts += 1
            date = Path(dt.strftime(check_date, self.date_fmt))
            date_dir = self.base / date
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
                    err(f"No new cases in {search_limit} days.", 127)

    def log(self, case: str, note_text: str) -> None:
        """Logs a timestamped note to an open case."""
        # TODO: capture $USER in case_log() and new_case()
        # TODO: generalize around log/append operations on notes files
        case_dir = self.base / case
        if case_dir.exists():
            notes = case_dir / self.notes
            if notes.exists():
                timestamp = dt.strftime(dt.today(), "%X")
                with notes.open("a") as notes_file:
                    print(f"## {timestamp}: {note_text}", file=notes_file)
        else:
            err(f'The case "{case}" does not exist.', 127)

    def new(self, summary: str, date_override: str = "") -> None:
        """Allocates a new case ID and creates the appropriate folders."""
        if not summary:
            try:
                summary = input("Case Summary: ")
            except KeyboardInterrupt:
                summary = input("Please provide a Case Summary: ")

            if not summary:
                raise IncompleteCase()

        # if date_override is set use it's value, otherwise use today's date
        if date_override:
            date = date_override
        else:
            date = dt.strftime(dt.today(), self.date_fmt)

        # Initialize the casefile base directory if it doesn't exist
        if not self.base.exists():
            self.base.mkdir()
            print(f"Created CaseFile base at {self.base}")

        # Have we created cases today? If not, create a new date directory.
        date_dir = self.base / date
        if not date_dir.exists():
            date_dir.mkdir()
            print(f"First case for today, {date}\n")

        # Find the next case in the series
        for serial in self.series:
            case = date_dir / serial
            if not case.exists():
                case.mkdir()
                for directory in self.directories:
                    resource_dir = case / directory
                    resource_dir.mkdir()
                print(f"Case opened:\n\t{case}")
                break
            else:
                continue

        notes = case / self.notes
        # TODO: make TZ representation configurable (local or UTC)
        # TODO: annotate timestamp with TZ the stamp is in
        timestamp = dt.strftime(dt.today(), "%X")
        with notes.open("a") as notes_file:
            print(f"# {timestamp}:  {summary}", file=notes_file)
