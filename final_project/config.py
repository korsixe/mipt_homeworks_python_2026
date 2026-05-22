import os
import sys
from typing import Any

import yaml


def load_config() -> dict[str, Any]:
    cfg: dict[str, Any] = {}

    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    if os.path.exists(config_path):
        with open(config_path, encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        cfg.update(data)

    env_map = {
        'API_KEY': 'api_key',
        'API_HOST': 'api_host',
        'LIMIT_CHARS': 'limit_chars',
        'LIMIT_MESSAGE': 'limit_message',
        'TEMPERATURE': 'temperature',
    }
    for env_var, key in env_map.items():
        val = os.environ.get(env_var)
        if val is not None:
            cfg[key] = val

    if not cfg.get('api_key') or not cfg.get('api_host'):
        print('Ошибка: не заданы api_key и/или api_host.')
        print('Задайте переменные окружения API_KEY и API_HOST или создайте файл config.yaml.')
        sys.exit(1)

    if cfg.get('limit_chars') is not None:
        cfg['limit_chars'] = int(cfg['limit_chars'])
    else:
        cfg.pop('limit_chars', None)
    if cfg.get('limit_message') is not None:
        cfg['limit_message'] = int(cfg['limit_message'])
    else:
        cfg.pop('limit_message', None)
    if cfg.get('temperature') is not None:
        cfg['temperature'] = float(cfg['temperature'])
    else:
        cfg['temperature'] = 0.7

    return cfg
