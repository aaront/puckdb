import configparser
import os

import click

from . import __title__


def _get_config_file_path():
    return os.path.join(click.get_app_dir(__title__), 'config.ini')


def _read():
    conf_file = _get_config_file_path()
    conf = configparser.RawConfigParser()
    try:
        conf.read(conf_file)
        return conf, conf_file
    except IOError:
        raise IOError('Could not find settings file.\n'
                      'Make sure it exists at "{path}"'.format(path=conf_file))


def _write(dsn=''):
    conf_file = _get_config_file_path()
    conf = configparser.RawConfigParser()
    if 'db' not in conf.sections():
        conf.add_section('db')
    conf.set('db', 'dsn', dsn)
    with open(conf_file, 'w') as f:
        conf.write(f)


def init():
    config_file = _get_config_file_path()
    if not os.path.exists(os.path.dirname(config_file)):
        os.makedirs(os.path.dirname(config_file))
        _write()


def get_db() -> str:
    dsn = os.getenv('PUCKDB_DATABASE', None)
    if dsn:
        return dsn
    config, config_file = _read()
    try:
        return config.get('db', 'dsn')
    except configparser.NoSectionError:
        raise IOError('Could not read database settings from the config file.\n'
                      'Make sure the [db] section exists in "{path}"'.format(path=config_file))
    except configparser.NoOptionError:
        raise IOError('Could not read database settings from the config file.\n'
                      'Make sure the [db] has the proper headings in "{path}"'.format(path=config_file))
