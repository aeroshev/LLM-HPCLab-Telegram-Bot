from typing import Final

DEFAULT_MESSAGE_TEMPLATE: Final[str] = "<s>{role}\n{content}</s>\n"
DEFAULT_SYSTEM_PROMPT: Final[str] = "Ты — Сайга, русскоязычный автоматический ассистент. Ты разговариваешь с людьми и помогаешь им."

class Conversation:

    def __init__(
        self,
        message_template: str = DEFAULT_MESSAGE_TEMPLATE,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        start_token_id: int = 1,
        bot_token_id: int = 9225
    ) -> None:
        self.message_template: str = message_template
        self.start_token_id: int = start_token_id
        self.bot_token_id: int = bot_token_id
        self.messages: list[dict[str, str]] = [{
            "role": "system",
            "content": system_prompt
        }]

    def get_start_token_id(self) -> int:
        return self.start_token_id

    def get_bot_token_id(self) -> int:
        return self.bot_token_id

    def add_user_message(self, message: str) -> None:
        self.messages.append({
            "role": "user",
            "content": message
        })

    def add_bot_message(self, message: str) -> None:
        self.messages.append({
            "role": "bot",
            "content": message
        })

    def get_prompt(self, tokenizer) -> str:
        final_text: str = ""
        for message in self.messages:  # type: dict[str, str]
            message_text: str = self.message_template.format(**message)
            final_text += message_text
        final_text += tokenizer.decode([self.start_token_id, self.bot_token_id])
        return final_text.strip()
