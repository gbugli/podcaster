import json
import os
from pathlib import Path

class Config:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._load_config()
        return cls._instance

    @classmethod
    def _load_config(cls):
        config_path = Path(__file__).parent.parent / 'config.json'
        print(config_path)
        with open(config_path) as f:
            cls._config = json.load(f)

    @classmethod
    def get(cls, key, default=None):
        if cls._config is None:
            cls._load_config()
        return cls._config.get(key, default)

    @classmethod
    def get_nested(cls, *keys, default=None):
        if cls._config is None:
            cls._load_config()
        
        value = cls._config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key, default)
            else:
                return default
        return value

config = Config()