import time
import os
import platform
import sys
import threading


class PlatformInfo:
    def __init__(self):
        self.system = platform.system()
        self.machine = platform.machine()
        self.processor = platform.processor()
        self.python_version = platform.python_version()
        self.distro_name = self._detect_distro()
        self.distro_id = self._detect_distro_id()
        self.is_windows = self.system == "Windows"
        self.is_linux = self.system == "Linux"
        self.is_macos = self.system == "Darwin"
        self.is_64bit = platform.architecture()[0] == "64bit"
        self.cpu_count = os.cpu_count() or 1
        self.home_dir = os.path.expanduser("~")
        self.config_dir = self._get_config_dir()

    def _detect_distro(self):
        if not self.is_linux:
            return self.system

        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=", 1)[1].strip().strip('"')
        except FileNotFoundError:
            pass

        try:
            with open("/etc/lsb-release", "r") as f:
                for line in f:
                    if line.startswith("DISTRIB_DESCRIPTION="):
                        return line.split("=", 1)[1].strip().strip('"')
        except FileNotFoundError:
            pass

        return "Unknown Linux"

    def _detect_distro_id(self):
        if not self.is_linux:
            return self.system.lower()

        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("ID="):
                        return line.split("=", 1)[1].strip().strip('"')
        except FileNotFoundError:
            pass

        return "unknown"

    def _get_config_dir(self):
        if self.is_windows:
            base = os.environ.get("APPDATA", self.home_dir)
            return os.path.join(base, "fugora")
        elif self.is_macos:
            return os.path.join(self.home_dir, "Library", "Application Support", "fugora")
        else:
            xdg = os.environ.get("XDG_CONFIG_HOME", os.path.join(self.home_dir, ".config
