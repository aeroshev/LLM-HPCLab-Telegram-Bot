import os
from typing import Final
from pathlib import Path

from yaml import load, CLoader

SECRETS_FOLDER: Final[Path] = Path('/run/secrets') if os.path.exists('/run/secrets') else (Path.home() / 'projects' / 'LLM-HPCLab-Telegram-Bot')

PATH_SECRETS: Final[str] = SECRETS_FOLDER / 'vault-secrets.yml'

with open(PATH_SECRETS.resolve(), mode='r') as file:
    _data: dict[str, str] = load(file, Loader=CLoader)

BOT_TOKEN: Final[str] = _data['bot_token']

