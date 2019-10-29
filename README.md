# CaseFile: simple text-based case management utility
CaseFile seeks to be simple and disposable (i.e. as long as you can read the
file system, some other tool you have will be able to read out organizational
system).  Each date gets a directory, and each case serial gets it's own
directory -- this is the casefile.


## Requirements
CaseFile only supports Python 3 and has no dependencies on code outside the
python standard library. This tool is tested and developed primarily on Linux,
but explicit support for macOS is forthcoming.

## Installation

    $ python setup.py install --user

I prefer `--user` installs, you might not! Either should work.

The installed command is `cf`.

## Usage

    $ cf new "There's something strange in the neighborhood..."
    $ cf -l

## Configuration
The default configuration is in `$XDG_CONFIG_HOME/casefile.ini` and it looks
like this:

    [casefile]
    base = /home/guest/cases
    case_directories = raw,processed
    case_series = ABCDEFGHIJKLMNOPQRSTUVWXYZ
    date_fmt = %Y-%m-%d
    notes_file = notes.md

A configuration can be overrode by placing a `casefile.ini` in your `$PWD`.

### base
This defines the base path for creating cases.

### case_firectories
These are subdirectories to create in a new casefile.

### case_series
By default casefile will create a case named by the date followed by a serial
within the `base` directory in short: `date_fmt/case_series[0]` would be the
first serial.

### date_fmt
This defines the format for the date using standard `strftime` formats.

## notes_file
The file CaseFile will write the creation timestamp and summary.
