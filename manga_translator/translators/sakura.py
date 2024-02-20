from typing import List
import os
from llama_cpp import Llama
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
from tqdm import tqdm

from .common import OfflineTranslator

# Adapted from:
# https://github.com/SakuraLLM/Sakura-13B-Galgame

def contains_japanese(text):
    for char in text:
        if '\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF':
            return True
    return False

class SakuraTranslator(OfflineTranslator):
    """Sakura translator based on Sakura13B large language model.
    Now the inference backend has been implemented contain:
    a) llama.cpp (with metal support)
    """

    _MODEL_SUB_DIR = os.path.join(OfflineTranslator._MODEL_SUB_DIR, "sakura")
    _MODEL_MAPPING = {
        "model": {
            "url": "https://huggingface.co/SakuraLLM/Sakura-13B-LNovel-v0.9b-GGUF/resolve/main/sakura-13b-lnovel-v0.9b-Q5_K_M.gguf",
            "hash": "ab7defef3d88ba25ce7177b0604eaad86872a32ba97c2ff7ebce27e018e3f44a",
        },
    }
    _MODEL_VERSION = "0.9"
    _SAKURA_MODEL_NAME = 'sakura-13b-lnovel-v0.9b-Q5_K_M.gguf'
    _TEXT_LENGTH = 512

    async def _load(self, from_lang: str, to_lang: str, device: str):
        self.load_params = {
            "from_lang": from_lang,
            "to_lang": to_lang,
            "device": device,
        }
        print('Llama: ', self._get_file_path(), 'device: ', device)
        n_gpu_layers = -1 if device != "cpu" else 0
        self.model = Llama(
            model_path=self._get_file_path(self._SAKURA_MODEL_NAME),
            n_gpu_layers=n_gpu_layers,
            n_ctx=4 * self._TEXT_LENGTH,
            n_threads=6,
            verbose=True,
            device=device
        )

    async def _unload(self):
        del self.model

    async def _infer(
        self, from_lang: str, to_lang: str, queries: List[str]
    ) -> List[str]:
        generation_config = GenerationConfig(
            temperature=0.1,
            top_p=0.3,
            top_k=40,
            num_beams=1,
            bos_token_id=1,
            eos_token_id=2,
            pad_token_id=0,
            max_new_tokens=512,
            min_new_tokens=1,
            do_sample=True,
            repetition_penalty=1.0,
            frequency_penalty=0.05,
        )

        tokenizer = None

        data = []
        for d in tqdm(queries):
            if(not contains_japanese(d)):
                data.append(d)
                continue
            prompt = self.get_prompt(d, self._MODEL_VERSION)
            output = self.get_model_response(
                self.model,
                tokenizer,
                prompt,
                self._MODEL_VERSION,
                generation_config,
                self._TEXT_LENGTH,
                True,
            )
            output.strip()
            # trancated chaos reput
            output = output[: 2 * len(d)]
            data.append(output.strip())

        return data

    def get_prompt(self, input, model_version="0.9"):
        if model_version == "0.5" or model_version == "0.9":
            prompt = "<|im_start|>system\n你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。<|im_end|>\n<|im_start|>user\n将下面的日文文本翻译成中文：" + input + "<|im_end|>\n<|im_start|>assistant\n"
            return prompt
        raise ValueError()

    def get_model_response(
        self,
        model: AutoModelForCausalLM,
        tokenizer: AutoTokenizer,
        prompt: str,
        model_version: str,
        generation_config: GenerationConfig,
        text_length: int,
        llama_cpp: bool = True,
        use_llm_sharp: bool = False,
    ):
        backup_generation_config_stage2 = GenerationConfig(
            temperature=0.1,
            top_p=0.3,
            top_k=40,
            num_beams=1,
            bos_token_id=1,
            eos_token_id=2,
            pad_token_id=0,
            max_new_tokens=text_length,
            min_new_tokens=1,
            do_sample=True,
            repetition_penalty=1.0,
            frequency_penalty=0.05,
        )

        backup_generation_config_stage3 = GenerationConfig(
            temperature=0.1,
            top_p=0.3,
            top_k=40,
            num_beams=1,
            bos_token_id=1,
            eos_token_id=2,
            pad_token_id=0,
            max_new_tokens=text_length,
            min_new_tokens=1,
            do_sample=True,
            repetition_penalty=1.0,
            frequency_penalty=0.2,
        )

        backup_generation_config = [
            backup_generation_config_stage2,
            backup_generation_config_stage3,
        ]

        def generate(model, generation_config):
            if "frequency_penalty" in generation_config.__dict__.keys():
                output = model(
                    prompt,
                    max_tokens=generation_config.__dict__["max_new_tokens"],
                    temperature=generation_config.__dict__["temperature"],
                    top_p=generation_config.__dict__["top_p"],
                    repeat_penalty=generation_config.__dict__["repetition_penalty"],
                    frequency_penalty=generation_config.__dict__["frequency_penalty"],
                )
            else:
                output = model(
                    prompt,
                    max_tokens=generation_config.__dict__["max_new_tokens"],
                    temperature=generation_config.__dict__["temperature"],
                    top_p=generation_config.__dict__["top_p"],
                    repeat_penalty=generation_config.__dict__["repetition_penalty"],
                )
            return output

        stage = 0
        output = generate(model, generation_config)
        while output["usage"]["completion_tokens"] == text_length:
            stage += 1
            if stage > 2:
                print("model degeneration cannot be avoided.")
                break
            print("model degeneration detected, retrying...")
            output = generate(model, backup_generation_config[stage - 1])
        response = output["choices"][0]["text"]
        return response

    def supports_languages(
        self, from_lang: str, to_lang: str, fatal: bool = False
    ) -> bool:
        return from_lang == 'JPN' and to_lang == 'CHS'
