from typing import Final

import torch
from peft import PeftModel, PeftConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, BitsAndBytesConfig

from .conversion import Conversation

MODEL_NAME: Final[str] = "IlyaGusev/saiga2_7b_lora"
BASE_MODEL_PATH: Final[str] = "TheBloke/Llama-2-7B-fp16"


class ModelInference:

    def __init__(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)

        quantization_config: BitsAndBytesConfig = BitsAndBytesConfig(
            load_in_4bit=True
        )

        config = PeftConfig.from_pretrained(MODEL_NAME)
        self.model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_PATH,
            torch_dtype=torch.float16,
            device_map="auto",
            quantization_config=quantization_config
        )
        self.model = PeftModel.from_pretrained(
            self.model,
            MODEL_NAME,
            torch_dtype=torch.float16
        )
        self.model.eval()

        self.generation_config = GenerationConfig.from_pretrained(MODEL_NAME)
    
    def generate(self, prompt: str) -> str:
        data = self.tokenizer(prompt, return_tensors="pt")
        data = {k: v.to(self.model.device) for k, v in data.items()}
        output_ids = self.model.generate(
            **data,
            generation_config=self.generation_config
        )[0]
        output_ids = output_ids[len(data["input_ids"][0]):]
        output = self.tokenizer.decode(output_ids, skip_special_tokens=True)
        return output.strip()
    
    async def answer(self, input: str) -> str:
        conversation = Conversation()
        conversation.add_user_message(input)
        prompt = conversation.get_prompt(self.tokenizer)

        output = await self.generate(self.model, self.tokenizer, prompt, self.generation_config)
        return output