from typing import List
from tqdm import tqdm


import requests

from .common import OfflineTranslator

# Adapted from:
# https://github.com/SakuraLLM/Sakura-13B-Galgame

def contains_japanese(text):
    for char in text:
        if '\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF':
            return True
    return False


class SakuraServerTranslator(OfflineTranslator):
    """Sakura translator based on Sakura13B large language model.
    """

    async def _load(self, from_lang: str, to_lang: str, device: str):
        self.load_params = {
            "from_lang": from_lang,
            "to_lang": to_lang,
            "device": device,
        }
        self.session = requests.Session()
        self.endpoint = "http://localhost:5000/api/v1/generate"

    async def _unload(self):
        pass
        
    async def _unload(self):
        pass

    async def _infer(
        self, from_lang: str, to_lang: str, queries: List[str]
    ) -> List[str]:
        data = []
        for d in tqdm(queries):
            if(not contains_japanese(d)):
                data.append(d)
                continue
            prompt = "<|im_start|>system\n你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。<|im_end|>\n" + "<|im_start|>user\n将下面的日文文本翻译成中文：" + d + "<|im_end|>\n" + "<|im_start|>assistant\n" 
            request = {
                "prompt": prompt,
                # 'temperature': 0.1,
                # 'top_p': 0.3,
                # 'top_k': 40,
                # 'num_beams': 1,
                'bos_token_id': 1,
                'eos_token_id': 2,
                'pad_token_id': 0,
                # 'max_new_tokens': 512,
                # 'min_new_tokens': 1,
                # 'do_sample': True,
                # 'repetition_penalty': 1.0,
                # 'frequency_penalty': 0.05,
                # 'stream': False,
                "auto_max_new_tokens": False,
                "max_tokens_second": 0,
                "preset": "None",
                "max_new_tokens": 512,
                "min_new_tokens": 1,
                "do_sample": True,
                "temperature": 0.1,
                "top_p": 0.3,
                "repetition_penalty": 1.0,
                "num_beams": 1,
                "typical_p": 1,
                "epsilon_cutoff": 0,  # In units of 1e-4
                "eta_cutoff": 0,  # In units of 1e-4
                "tfs": 1,
                "top_a": 0,
                "presence_penalty": 0,
                "frequency_penalty": 0.05,
                "repetition_penalty_range": 0,
                "top_k": 40,
                "min_length": 0,
                "no_repeat_ngram_size": 0,
                "penalty_alpha": 0,
                "length_penalty": 1,
                "early_stopping": False,
                "mirostat_mode": 0,
                "mirostat_tau": 5,
                "mirostat_eta": 0.1,
                "grammar_string": "",
                "guidance_scale": 1,
                "negative_prompt": "",
                "seed": -1,
                "add_bos_token": True,
                "truncation_length": 2048,
                "ban_eos_token": False,
                "custom_token_bans": "",
                "skip_special_tokens": True,
                "stopping_strings": [],
            }
            response = self.session.post(self.endpoint, json=request)
            result = response.json()
            output = result["results"][0]["text"]
            output.strip()
            # trancated chaos reput
            output = output[: 2 * len(d)]
            data.append(output.strip())
        return data



    def supports_languages(
        self, from_lang: str, to_lang: str, fatal: bool = False
    ) -> bool:
        return from_lang == 'JPN' and to_lang == 'CHS'
