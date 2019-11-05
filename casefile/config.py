# Copyright (C) 2017-2019 Max R.D. Parmer
# License AGPLv3+: GNU Affero GPL version 3 or later.
# http://www.gnu.org/licenses/agpl.html

from configparser import ConfigParser
from functools import partial
from os import getenv
from pathlib import Path
from string import ascii_uppercase
from sys import platform


# Defines a specialized CasefileConfigParser with interpolation disabled
CasefileConfigParser = partial(ConfigParser,
                               interpolation=None)


def find_config(config_name='casefile.ini'):
    xdg_cfg_home = getenv('XDG_CONFIG_HOME')
    dot_config = Path.home() / '.config'
    local_config = Path.cwd() / config_name

    if xdg_cfg_home:
        cfg = Path(xdg_cfg_home) / config_name
    elif dot_config.exists():
        cfg = dot_config / config_name
    elif platform.startswith('linux') or ('bsd' in platform):
        cfg = Path.home() / f'.{config_name}'
    elif platform.startswith('darwin'):
        cfg = Path.home() / 'Library' / 'Application Support' / \
                'is.trystero.CaseFile' / config_name
    else:
        raise Exception(f'{platform} support is not implemented.')

    # Or override it all with a local config
    if local_config.exists():
        cfg = local_config

    return cfg


def _input_or_default(prompt, default):
    userval = input(f'{prompt}? [{default}]: ')
    if not userval:
        return default
    else:
        if userval.lower() in ['y', 'yes', 'si', 'sure']:
            userval = True
        elif userval.lower in ['n', 'no']:
            userval = False
        return userval


def write_config(config_file):
    init = f'Would you like to create the configuration file "{config_file}"'
    if _input_or_default(init, 'Yes'):
        if not config_file.parent.exists():
            config_file.parent.mkdir()

        with config_file.open('w') as new_config_file:
            config = CasefileConfigParser()
            config['casefile'] = {
                'base':
                    _input_or_default('CaseFile Base', Path.home() / 'cases'),
                'case_directories':
                    _input_or_default('Case Directories', 'raw,processed'),
                'case_series':
                    _input_or_default('Case Serial Series', ascii_uppercase),
                'date_fmt':
                    _input_or_default('Date Format', '%Y-%m-%d'),
                'notes_file':
                    _input_or_default('Notes File', 'notes.md'),
            }
            if _input_or_default('Configure Jira?', 'No'):
                jira = {
                    'jira_user':
                        input('Jira user (user@domain): '),
                    'jira_key':
                        input('Jira REST API key: '),
                    'jira_proj':
                        input('Jira project to post cases in: '),
                    'jira_type':
                        input('Jira issue type: '),
                    'jira_domain':
                        input('Jira domain (e.g. evilcorp.atlassian.net): ')
                }
                config['casefile'].update(jira)
            config.write(new_config_file)

        print(f'Created CaseFile configuration in {config_file}')
        return config_file


def read_config(config_file=None):
    """Try to read the configuration file, and if this fails
    write out a default config.
    """
    config = CasefileConfigParser()
    with config_file.open('r') as cfg:
        config.read_file(cfg)

    return config
