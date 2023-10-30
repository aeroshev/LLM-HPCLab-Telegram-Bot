from typing import Final

import torch
from peft import PeftConfig, PeftModel
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BatchEncoding,
    BitsAndBytesConfig,
    GenerationConfig,
    LlamaModel,
    LlamaPreTrainedModel,
    LlamaTokenizerFast,
)

from hpc_bot.metrics import REQUEST_TIME
from hpc_bot.model.conversion import Conversation

MODEL_NAME: Final[str] = "IlyaGusev/saiga_mistral_7b"


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
        # Загрузить токенизатора Mistral
        self.tokenizer: LlamaTokenizerFast = AutoTokenizer.from_pretrained(
            MODEL_NAME,
            use_fast=True,
            legacy=False
        )

        # Загрузить модель Mistral 7B
        quantization_config: BitsAndBytesConfig = BitsAndBytesConfig(
            load_in_4bit=True
        )
        config: PeftConfig = PeftConfig.from_pretrained(MODEL_NAME)
        self.model: LlamaPreTrainedModel = AutoModelForCausalLM.from_pretrained(
            config.base_model_name_or_path,
            torch_dtype=torch.float32,
            device_map="auto",
            quantization_config=quantization_config
        )
        self.model: LlamaModel = PeftModel.from_pretrained(
            self.model,
            MODEL_NAME,
            torch_dtype=torch.float32
        )
        self.model.eval()

        # Конфиг генерации
        self.generation_config: GenerationConfig = GenerationConfig.from_pretrained(MODEL_NAME)

    def generate(self, prompt: str) -> str:
        """
        Сгенерировать ответ модели.
        :param prompt: входной промпт модели.
        :return: ответ модели в формате строки.
        """
        data: BatchEncoding = self.tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
        with torch.no_grad():
            data = {k: v.to(self.model.device) for k, v in data.items()}
            output_ids = self.model.generate(
                **data,
                generation_config=self.generation_config
            )[0]
        output_ids = output_ids[len(data["input_ids"][0]):]
        output = self.tokenizer.decode(output_ids, skip_special_tokens=True)
        return output.strip()

    @REQUEST_TIME.time()
    def __call__(self, сonversation: Conversation) -> str:
        """
        Подготовить промпт для модели из истории диалога и запросить ответ.
        :param input: новый запрос от пользователя.
        :param chat_id: индефикатор чата, для различия пользователей.
        :return: ответ модели в формате строки.
        """
        prompt = сonversation.get_prompt()
        output = self.generate(prompt)
        return output
