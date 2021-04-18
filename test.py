import os

from pathlib import Path
from unittest.mock import patch

import pytest

from casefile.config import find_config, write_config
from casefile.errors import UnsupportedPlatform


class TestConfig:
    """Test casefile.config components"""

    config_file = "casefile.ini"

    def test_xdg_find_config(self, tmpdir):
        """Test config discovery on linux under XDG"""
        expected_config = tmpdir / self.config_file

        with patch("casefile.config.platform", "linux"):
            # assuming linux (or bsd...)
            with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(tmpdir)}):
                config_path = find_config()

        assert config_path == expected_config

    def test_home_find_dotconfig(self, tmpdir):
        """Test discovery of ~/.config/casefile.ini"""
        expected_config = tmpdir.mkdir(".config") / self.config_file
        expected_config.write("test")

        with patch("casefile.config.platform", "linux"):
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

    def test_find_macos_native_config(self, tmpdir):
        """Test discovery of $PWD/casefile.ini"""
        expected_config = (
            Path.home()
            / "Library"
            / "Application Support"
            / "is.trystero.CaseFile"
            / self.config_file
        )

        with patch("casefile.config.platform", "darwin"):
            config_path = find_config()

        assert config_path == expected_config

    def test_unsupported_platform_config(self):
        """Test rejection of unsupported platforms."""
        with pytest.raises(UnsupportedPlatform):
            with patch("casefile.config.platform", "win32"):
                find_config()

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
