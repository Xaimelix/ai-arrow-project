import base64
import json
import random
import requests
import csv
from speechkit import configure_credentials, creds, model_repository


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
            "modelUri": f"gpt://{self.catalog}/yandexgpt/latest",
            "completionOptions": {
                "stream": False,
                "temperature": 0.3,
                "maxTokens": "300"
            },
            "messages": [
                {
                    "role": "system",
                    "text": "Ты находишься во вселенной Dungeons & Dragons. Ответы должны быть краткими. Дополняй мой ответ, детализируя окружающую среду и атмосферу. Описывай обстановку, но не придумывай новых действий."
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
        configure_credentials(
        yandex_credentials=creds.YandexCredentials(
            api_key=self.apikey
            )
        )

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
        # self.prompt_text['completionOptions']['temperature'] = random.uniform(0.2, 0.8)

        response = requests.post(url, headers=headers, json=self.prompt_text)
        return response.text
    
    def GPT_ART_response(self, response) -> str:
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/imageGenerationAsync"
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

    def speech_synthesis(self, text):
        # url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
        # headers = {
        #     "Authorization": f"Api-Key {self.apikey}",
        #     "x-folder-id": self.identifier
        # }
        # response = requests.post(url, headers=headers, 
        #                         json={"text": text,
        #                             "outputAudioSpec": {
        #                             "containerAudio": {
        #                                 "containerAudioType": "OGG_OPUS",
        #                             }},
        #                             "hints": [
        #                             {"speed": "1"}, 
        #                             {"voice": "anton"}, 
        #                             {"role": "neutral"}, 
        #                             {"unsafe_mode": "true"}]})
        model = model_repository.synthesis_model()
        model.voice = 'anton'
        response = model.synthesize(text, raw_format=False)
        return response

