import os
from typing import Final

from yaml import load, CLoader

PATH_SECRETS: Final[str] = '/run/secrets/bot-secrets' if os.path.exists('/run/secrets/bot-secrets') else '../vault-secrets.yml'

with open(PATH_SECRETS, mode='r') as file:
    _data: dict[str, str] = load(file, Loader=CLoader)

BOT_TOKEN: Final[str] = _data['bot_token']

