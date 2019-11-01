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
        cfg = Path.home() / 'Library' / 'is.trystero.CaseFile' / config_name
    else:
        raise Exception(f'{platform} support is not implemented.')

    # Or override it all with a local config
    if local_config.exists():
        cfg = local_config

    return cfg


def _write_config():
    default_config = find_config()

    if not default_config.parent.exists():
        default_config.parent.mkdir()

    with default_config.open('w') as new_config_file:
        config = CasefileConfigParser()
        config['casefile'] = {
            'base': Path.home() / 'cases',
            'case_directories': 'raw,processed',
            'case_series': ascii_uppercase,
            'date_fmt': '%Y-%m-%d',
            'notes_file': 'notes.md',
        }
        config.write(new_config_file)

    print(f'Created default config in {default_config}')
    return default_config


def read_config():
    """Try to read the configuration file, and if this fails
    write out a default config.
    """
    try:
        config_file = find_config()
    except:
        raise
    finally:
        try:
          # try to create a config
          config_file = _write_config()
        except:
          raise

    config = CasefileConfigParser()
    with config_file.open('r') as cfg:
        config.read_file(cfg)

    return config
