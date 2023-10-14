from typing import Final

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, BitsAndBytesConfig

from model.conversion import Conversation

MODEL_NAME: Final[str] = "IlyaGusev/saiga2_7b_lora"
BASE_MODEL_PATH: Final[str] = "TheBloke/Llama-2-7B-fp16"


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
    
    def __call__(self, сonversation: Conversation) -> str:
        """
        Подготовить промпт для модели из истории диалога и запросить ответ.
        :param input: новый запрос от пользователя.
        :param chat_id: индефикатор чата, для различия пользователей.
        :return: ответ модели в формате строки.
        """
        prompt = сonversation.get_prompt(self.tokenizer)
        output = self.generate(prompt)
        return output