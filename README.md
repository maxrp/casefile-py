# CaseFile: simple text-based case management utility
CaseFile seeks to be simple and disposable (i.e. as long as you can read the
file system, some other tool you have will be able to read out organizational
system).  Each date gets a directory, and each case serial gets it's own
directory -- this is the casefile.


## Requirements
CaseFile only supports Python 3 and has no dependencies on code outside the
python standard library. This tool is tested and developed primarily on Linux,
though macOS should also be well supported.

There is an optional dependency on the Requests library, if you would like Jira
integration.

## Installation
Download the latest [tag or release](https://github.com/maxrp/casefile-py/tags), unpack it, cd into it's directory then:

    $ pip install .

Or, if you'd like Jira support:

    $ pip install .[Jira]

I prefer `--user` installs, you might not! Either should work.

The installed command is `cf`.

## Usage


    $ cf new "There's something strange in the neighborhood..."
    $ cf -l

## Configuration
If you run the tool without a configuration created, it will guide you through
creating a new `casefile.ini`.

The default configuration is in `$XDG_CONFIG_HOME/casefile.ini` on most Linux
systems with a desktop environment. Typically this will be `~/.config/casefile.ini`
and it looks like this:

    [casefile]
    base = /home/guest/cases
    case_directories = raw,processed
    case_series = ABCDEFGHIJKLMNOPQRSTUVWXYZ
    date_fmt = %Y-%m-%d
    notes_file = notes.md

A configuration can be overrode by placing a `casefile.ini` in your `$PWD`.

Additionally, if you have the Jira feature enabled, you'll want to populate
these additional configuration keys:

    jira_user = maxp@pdx.edu
    jira_key = example-key-a-fake-key!!
    jira_proj = SECURITY
    jira_type = Incident
    jira_domain = evilcorp.atlassian.net

#### base
This defines the base path for creating cases.

#### case_directories
These are subdirectories to create in a new casefile.

#### case_series
By default casefile will create a case named by the date followed by a serial
within the `base` directory in short: `date_fmt/case_series[0]` would be the
first serial.

#### date_fmt
This defines the format for the date using standard `strftime` formats.

#### notes_file
The file CaseFile will write the creation timestamp and summary.

#### jira_user
Typically you@example.com, whatever you'd use for basic auth with the Jira REST
API.

#### jira_key
Your Jira REST API key.

#### jira_proj
The Jira project to use.

#### jira_type
The issue type to use when posting cases.

#### jira_domain
The Jira domain for your server or hosted instance.
