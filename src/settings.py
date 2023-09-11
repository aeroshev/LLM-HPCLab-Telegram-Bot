from typing import Final

from yaml import load, CLoader

with open('/run/secrets/bot-secrets') as file:
    _data: dict[str, str] = load(file, Loader=CLoader)

BOT_TOKEN: Final[str] = _data['bot_token']

