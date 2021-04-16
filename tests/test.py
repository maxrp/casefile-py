import os

from unittest import mock

from casefile.config import find_config

DEFAULT_CONF = "casefile.ini"


def test_xdg_find_config(tmpdir):
    """Test config discovery on linux under XDG"""
    expected_config = tmpdir / DEFAULT_CONF

    with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(tmpdir)}):
        config_path = find_config()

    assert config_path == expected_config


def test_home_find_dotconfig(tmpdir):
    """Test discovery of ~/.config/casefile.ini"""
    expected_config = tmpdir.mkdir(".config") / DEFAULT_CONF
    expected_config.write("test")

    with mock.patch.dict(os.environ, {"HOME": str(tmpdir)}):
        config_path = find_config()

    assert config_path == expected_config


def test_home_find_dotfile(tmpdir):
    """Test discovery of ~/.casefile.ini"""
    expected_config = tmpdir / f".{DEFAULT_CONF}"

    with mock.patch.dict(os.environ, {"HOME": str(tmpdir)}):
        config_path = find_config()

    assert config_path == expected_config
