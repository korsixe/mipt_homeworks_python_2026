import os
import sys
from typing import Any

import yaml

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config() -> dict[str, Any]:
    cfg: dict[str, Any] = {}

    config_path = os.path.join(_PROJECT_ROOT, 'config.yaml')
    if os.path.exists(config_path):
        try:
            with open(config_path, encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            cfg.update(data)
        except (OSError, yaml.YAMLError) as e:
            print(f'Ошибка чтения config.yaml: {e}')
            sys.exit(1)

    env_map = {
        'API_KEY': 'api_key',
        'API_HOST': 'api_host',
        'LIMIT_CHARS': 'limit_chars',
        'LIMIT_MESSAGE': 'limit_message',
        'TEMPERATURE': 'temperature',
        'STREAM': 'stream',
    }
    for env_var, key in env_map.items():
        val = os.environ.get(env_var)
        if val is not None:
            cfg[key] = val

    if not cfg.get('api_key') or not cfg.get('api_host'):
        print('Ошибка: не заданы api_key и/или api_host.')
        sys.exit(1)

    if cfg.get('limit_chars') is not None:
        try:
            cfg['limit_chars'] = int(cfg['limit_chars'])
        except (ValueError, TypeError):
            print('Ошибка: limit_chars должен быть целым числом.')
            sys.exit(1)
    else:
        cfg.pop('limit_chars', None)

    if cfg.get('limit_message') is not None:
        try:
            cfg['limit_message'] = int(cfg['limit_message'])
        except (ValueError, TypeError):
            print('Ошибка: limit_message должен быть целым числом.')
            sys.exit(1)
        if cfg['limit_message'] <= 0:
            print('Ошибка: limit_message должен быть положительным числом.')
            sys.exit(1)
    else:
        cfg.pop('limit_message', None)

    if cfg.get('temperature') is not None:
        try:
            cfg['temperature'] = float(cfg['temperature'])
        except (ValueError, TypeError):
            print('Ошибка: temperature должен быть числом.')
            sys.exit(1)
    else:
        cfg['temperature'] = 0.7

    if 'stream' in cfg:
        val = cfg['stream']
        if not isinstance(val, bool):
            cfg['stream'] = str(val).lower() in ('1', 'true', 'yes')
    else:
        cfg['stream'] = False

    return cfg
