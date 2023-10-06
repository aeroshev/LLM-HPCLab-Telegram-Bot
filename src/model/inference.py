from typing import Final
from datetime import datetime, timedelta

import torch
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, BitsAndBytesConfig
from cachetools import TTLCache

from .conversion import Conversation
from metrics import CHAT_COUNTS, REQUEST_TIME, DEPTH_CONVERSION

MODEL_NAME: Final[str] = "IlyaGusev/saiga2_7b_lora"
BASE_MODEL_PATH: Final[str] = "TheBloke/Llama-2-7B-fp16"


def track_depth(cache: TTLCache) -> None:
    """Отслеживание глубины каждого чата"""
    for record_key in cache:
        DEPTH_CONVERSION.labels(f'{record_key}').set(len(cache[record_key]))


CONVERSION_CACHE: TTLCache = TTLCache(
    maxsize=10,
    ttl=timedelta(hours=12),
    timer=datetime.now
)
CHAT_COUNTS.set_function(lambda: len(CONVERSION_CACHE))


class ModelInference:
    """
    Инференс модели для старта модели и взаимодействия с ней.
    """
    __slots__ = (
        'tokenizer',
        'model',
        'generation_config'
    )

    def __init__(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME,
            use_fast=True,
            legacy=False
        )

        quantization_config: BitsAndBytesConfig = BitsAndBytesConfig(
            load_in_4bit=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_PATH,
            torch_dtype=torch.float32,
            device_map="auto",
            quantization_config=quantization_config
        )
        self.model = PeftModel.from_pretrained(
            self.model,
            MODEL_NAME,
            torch_dtype=torch.float32
        )
        self.model.eval()

        self.generation_config = GenerationConfig.from_pretrained(MODEL_NAME)
    
    def generate(self, prompt: str) -> str:
        """
        Сгенерировать ответ модели.
        :param prompt: входной промпт модели.
        :return: ответ модели в формате строки.
        """
        data = self.tokenizer(prompt, return_tensors="pt")
        data = {k: v.to(self.model.device) for k, v in data.items()}
        output_ids = self.model.generate(
            **data,
            generation_config=self.generation_config
        )[0]
        output_ids = output_ids[len(data["input_ids"][0]):]
        output = self.tokenizer.decode(output_ids, skip_special_tokens=True)
        return output.strip()
    
    @REQUEST_TIME.time()
    def __call__(self, input: str, chat_id: int) -> str:
        """
        Подготовить промпт для модели из истории диалога и запросить ответ.
        :param input: новый запрос от пользователя.
        :param chat_id: индефикатор чата, для различия пользователей.
        :return: ответ модели в формате строки.
        """
        if not CONVERSION_CACHE.get(chat_id):
            conversation = Conversation()
            CONVERSION_CACHE[chat_id] = conversation
        else:
            conversation = CONVERSION_CACHE[chat_id]
        track_depth(CONVERSION_CACHE)
        
        conversation.add_user_message(input)
        prompt = conversation.get_prompt(self.tokenizer)

        output = self.generate(prompt)
        return output