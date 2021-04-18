import os

from pathlib import Path
from unittest.mock import patch

import pytest

from casefile.config import find_config, write_config, read_config, _input_or_default
from casefile.errors import UnsupportedPlatform, err

# pylint: disable=R0201
class TestConfig:
    """Test casefile.config components"""

    config_file = "casefile.ini"

    @patch("casefile.config.platform", "linux")
    def test_xdg_find_config(self, tmpdir):
        """Test config discovery on linux under XDG"""
        expected_config = tmpdir / self.config_file

        with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(tmpdir)}):
            config_path = find_config()

        assert config_path == expected_config

    @patch("casefile.config.platform", "linux")
    def test_home_find_dotconfig(self, tmpdir):
        """Test discovery of ~/.config/casefile.ini"""
        expected_config = tmpdir.mkdir(".config") / self.config_file
        expected_config.write("test")

        with patch.dict(os.environ, {"HOME": str(tmpdir)}):
            config_path = find_config()

        assert config_path == expected_config

    def test_home_find_dotfile(self, tmpdir):
        """Test discovery of ~/.casefile.ini"""
        expected_config = tmpdir / f".{self.config_file}"

        with patch("casefile.config.platform", "linux"):
            with patch.dict(os.environ, {"HOME": str(tmpdir)}):
                config_path = find_config()

        assert config_path == expected_config

    @patch("casefile.config.platform", "darwin")
    def test_find_macos_native_config(self, tmpdir):
        """Test discovery of $PWD/casefile.ini"""

        with patch.dict(os.environ, {"HOME": str(tmpdir)}):
            expected_config = (
                Path.home()
                / "Library"
                / "Application Support"
                / "is.trystero.CaseFile"
                / self.config_file
            )
            config_path = find_config()

        assert config_path == expected_config

    def test_unsupported_platform_config(self):
        """Test rejection of unsupported platforms."""
        with pytest.raises(UnsupportedPlatform):
            with patch("casefile.config.platform", "win32"):
                find_config()

    def test_input_or_default_default_condition(self):
        """Ensure that _input_or_default allows users to accept the default."""
        fake_input = lambda _: ""
        with patch("casefile.config.input", side_effect=fake_input):

            default_str = "boop"
            assert default_str == _input_or_default("foo", "boop")

            default_bool = False
            assert default_bool == _input_or_default("bar", False)

            default_path = Path("/")
            assert default_path == _input_or_default("baz", default_path)

    def test_input_or_default_input_condition(self):
        """Ensure that _input_or_default allows users to provide input."""
        expected_response = "something inappropriate"
        fake_input = lambda _: expected_response
        with patch("casefile.config.input", side_effect=fake_input):

            default_str = "boop"
            assert expected_response == _input_or_default("foo", "boop")

            default_bool = False
            assert expected_response == _input_or_default("bar", False)

            default_path = Path("/")
            assert expected_response == _input_or_default("baz", default_path)

    @patch("casefile.config.platform", "linux")
    def test_config_write_config_bailout(self, tmpdir):
        """Ensure write_config accepts rejection."""
        with patch.dict(os.environ, {"HOME": str(tmpdir)}):
            with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(tmpdir)}):
                config_path = find_config()
                fake_input = lambda _: "n"

                with patch("casefile.config.input", side_effect=fake_input):
                    with pytest.raises(Exception):
                        write_config(config_path)

    @patch("casefile.config.platform", "darwin")
    def test_config_write_read_config_integration(self, tmpdir):
        """Ensure write_config produces a readable config and
        that the minimum required keys are present.

        The config subsystem needs to be rewritten so this is
        somewhat of a placeholder.
        """
        with patch.dict(os.environ, {"HOME": str(tmpdir)}):
            with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(tmpdir)}):
                config_path = find_config()
                fake_input = lambda _: ""

                with patch("casefile.config.input", side_effect=fake_input):
                    write_config(config_path)

        # If something's really screwed up, this'll throw an exception
        config = read_config(config_path)
        mandatory_keys = [
            "base",
            "case_directories",
            "case_series",
            "date_fmt",
            "notes_file",
        ]
        for key in mandatory_keys:
            assert config["casefile"].get(key, False) is not False


def test_err_func():
    """Test that err exits and respects the provided code."""
    with pytest.raises(SystemExit) as exit_condition:
        err("Byeee", 255)
    assert exit_condition.value.code == 255