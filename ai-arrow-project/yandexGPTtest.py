import base64
import json
import random
import requests
import csv

class StreamResponse:
    def __init__(self, catalog, identifier, apikey):
        """
        Функция инициализирует атрибуты, связанные с моделью Yandex GPT для генерации текста и картинок.
        """
        self.catalog = catalog
        self.identifier = identifier
        self.apikey = apikey
        with open('yandexGPTinfo.txt', 'r', encoding='utf-8') as file: 
            self.context1 = file.read() 
        with open('yandexGPTinfo1.txt', 'r', encoding='utf-8') as file:
            self.context2 = file.read()
        self.prompt_text = {
            "modelUri": f"gpt://{self.catalog}/yandexgpt-lite/latest",
            "completionOptions": {
                "stream": False,
                "temperature": 0.4,
                "maxTokens": "300"
            },
            "messages": [
                {
                    "role": "system",
                    "text": "Ты гейм мастер в игре 'Подземелья и драконы'. На ответ пользователя (действие) выдавай обыгрывай эту ситуацию. Отвечай одним действием среды." # !!! обязательно добавить запрет на запросы не по теме.
                },
                {
                    'role': 'system',
                    'text': 'Не рассказывай историю заранее. Не отвечай на вопросы не связанные с игрой.'
                }
            ]
        }
        self.prompt_art =  {
            "modelUri": f"art://{self.catalog}/yandex-art/latest",
            "generationOptions": {
            "seed": "183",
            "aspectRatio": {
                "widthRatio": "1",
                "heightRatio": "1"
            }
            },
            "messages": []
        }

    def GPT_text_response(self, history):
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.apikey}",
            "x-folder-id": self.identifier
        }
        self.history = history
        for dct in self.history:
            if dct['author'] == 'user':
                self.prompt_text['messages'].append({
                    "role": "user",
                    "text": dct['text']
                })
            elif dct['author'] == 'bot':
                self.prompt_text['messages'].append({
                    "role": "assistant",
                    "text": dct['text']
                })
        self.prompt_text['completionOptions']['temperature'] = random.uniform(0.2, 0.8)

        response = requests.post(url, headers=headers, json=self.prompt_text)
        return response.text
    
    def GPT_ART_response(self, response) -> str:
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/imageGenerationAsync"
        url1 = "https://llm.api.cloud.yandex.net:443/operations/"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.apikey}",
            "x-folder-id": self.identifier
        }
        self.prompt_art['messages'].append({"weight": '1', "text": response})
        response = json.loads(requests.post(url, headers=headers, json=self.prompt_art).text)
        try:
            response_id = response['id']
        except KeyError:
            return False
        return response_id
    
    def GPT_ART_ready_response(self, response_id) -> bytes:
        url = f"https://llm.api.cloud.yandex.net:443/operations/{response_id}"
        headers = {
            "Authorization": f"Api-Key {self.apikey}"
        }
        try:
            response = requests.get(url, headers=headers)
            image_base64 = response.json()['response']['image']
            image_bytes = base64.b64decode(image_base64)
        except KeyError as e:
            return False
        return image_bytes

