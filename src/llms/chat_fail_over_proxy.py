import json
import concurrent.futures

from logger import logging
from functools import partial
from openai import OpenAI
from constants import OPENAI_API_KEY,OPENAI_VERSION



class ChatFailOverProxy:
    def __init__(self):
        self.openAiClient = OpenAI(api_key=OPENAI_API_KEY)
    
    
    def generate(self, model: str, user_message: str,
                 max_tokens: int, temperature: float, format_: str,
                 timeout: int) -> str:
        models = [model] + [m for m in ["openAI", "amazonNova", "azureOpenAI"] if m != model]
        last_error = ""
        for m in models:
            try:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(partial(self.invoke_model_with_timeout, m, user_message,
                                                      max_tokens, temperature, format_, timeout))
                    return future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                last_error = f"Model {m} timed out"
                logging.info(last_error)
            except Exception as e:
                last_error = f"Model {m} failed: {str(e)}"
                logging.info(last_error)

        return f"Failed with all models: {last_error}"

    def invoke_model_with_timeout(self, model, user_message, max_tokens, temperature, format_, timeout):
        method = getattr(self, model)
        response = method(user_message, max_tokens, temperature, format_,timeout)
        return response

    def openAI(self, user_message, max_tokens, temperature, format_,timeout):
        response = self.openAiClient.chat.completions.create(
            model=OPENAI_VERSION,
            messages=[{"role":"system","content" : user_message }],
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout,
            response_format={"type" : format_})
        
        return response.choices[0].message.content

    def azureOpenAI(self, user_message, max_tokens, temperature, format_,timeout):
        return f"Simulated azureOpenAI response."

    def amazonNova(self, user_message, max_tokens, temperature, format_,timeout):
        return f"Simulated amazonNova response "

    def llama(self, user_message, max_tokens, temperature, format_,timeout):
        return f"Simulated llama response"

