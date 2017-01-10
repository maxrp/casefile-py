from configparser import ConfigParser
from os import getenv
from pathlib import Path


def _default_config_file(config_name='casefile.ini'):
    return Path(getenv('XDG_CONFIG_HOME', default=Path.home() / '.config' / config_name))

def _write_config():
    default_config = _default_config_file()

    if not default_config.parent.exists():
        default_config.parent.mkdir()

    with default_config.open('w') as new_config_file:
        config = ConfigParser()
        config['casefile'] = {
                'base': Path.home() / 'cases',
                'case_directories': ['raw', 'processed'],
                'notes': 'notes.md',
        }
        config.write(new_config_file)

    return default_config

def find_config(config_name='casefile.ini'):
    """Try to find a :config_name: in the default locations of
    ./:config_name: and failing that ~/$XDG_CONFIG_HOME/casefile.ini
    """
    default_configs = [Path.cwd() / config_name,
                       _default_config_file(config_name)]
    for config in default_configs:
        if config.exists():
            return config
    raise FileNotFoundError(default_configs[0])

def read_config():
    """Try to read the configuration file, and if this fails
    write out a default config.
    """
    config = ConfigParser()

    try:
        config_file = find_config()
    except FileNotFoundError:
        # try to create a config
        config_file = _write_config()
        print('Created default config in {}'.format(config_file))

    with config_file.open('r') as cf:
        config.read(cf)

    return config
