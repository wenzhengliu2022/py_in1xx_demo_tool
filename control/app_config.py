import configparser
import platform
from pathlib import Path
from typing import Any, Dict, Optional


class AppConfig:
    def __init__(self, app_name: str):
        self.itf = "ble"
        self.target = "C6:D5:02:A0:02:01"
        self.company_id = 0xf119
        self.data_endian = "little"
        self.data_offset = 11
        self.temp_slope = 0.0078125
        self.temp_offset = 0.0

        self.app_name = app_name
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "app_cfg.ini"
        print(self.config_file)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config = configparser.ConfigParser()
        self._load_config()

    def _get_config_dir(self) -> Path:
        system = platform.system()
        if system == "Darwin":  # macOS
            return Path.home() / "Documents" / self.app_name
        elif system == "Windows":
            return Path.home() / "AppData" / "Local" / self.app_name
        else:  # Linux
            return Path.home() / ".config" / self.app_name

    def _load_config(self):
        if self.config_file.exists():
            self.config.read(self.config_file)
            self.data_endian = self.config['TEMP']['data_endian']
            print(self.data_endian)
            data_offset = self.config['TEMP']['data_offset']
            self.data_offset = int(data_offset)

            temp_slope = self.config['TEMP']['temp_slope']
            print(temp_slope)
            self.temp_slope = float(temp_slope)
            print(self.temp_slope)

            temp_offset = self.config['TEMP']['temp_offset']
            self.temp_offset = float(temp_offset)

        else:
            self._create_default_config()

    def _create_default_config(self):
        self.config['APP'] = {
            # ble or uart
            'interface': self.itf,
        }

        self.config['BLE'] = {
            'target': self.target,
            'company_id': '0x{:04x}'.format(self.company_id),
        }

        self.config['UART'] = {
            'com': 'COM3',
            'baud_rate': '115200',
        }

        self.config['TEMP'] = {
            # big or little
            'data_endian': self.data_endian,
            'data_offset': str(self.data_offset),
            'temp_slope': str(self.temp_slope),
            'temp_offset': str(self.temp_offset),
        }

        self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            print(self.config_file)
            self.config.write(f)

    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        """获取配置值"""
        try:
            return self.config.get(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback

    def set(self, section: str, key: str, value: Any):
        """设置配置值"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        self.save_config()
