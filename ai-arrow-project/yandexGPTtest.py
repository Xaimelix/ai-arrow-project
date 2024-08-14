import requests
import csv

# def get_values_from_csv(file_path):
#     with open(file_path, mode='r', encoding='utf-8') as file:
#         reader = csv.DictReader(file)
        
#         catalog, identifier, apikey = None, None, None
#         for row in reader:
#             catalog = row['catalog']
#             identifier = row['identifier']
#             apikey = row['apikey']
#         return catalog, identifier, apikey


# file_path = 'ai-arrow-project/tokens.csv' 
# catalog, identifier, apikey = get_values_from_csv(file_path)

# prompt = {
#     "modelUri": f"gpt://{catalog}/yandexgpt-lite/latest",
#     "completionOptions": {
#         "stream": False,
#         "temperature": 0.6,
#         "maxTokens": "2000"
#     },
#     "messages": [
#         {
#             "role": "system",
#             "text": "Ты ассистент дроид, способный помочь в галактических приключениях, вселенной star wars"
#         },
#         {
#             "role": "user",
#             "text": "Привет, Дроид! Мне нужна твоя помощь, чтобы узнать больше о Силе. Как я могу научиться ее использовать?"
#         },
#         {
#             "role": "assistant",
#             "text": "Привет! Чтобы овладеть Силой, тебе нужно понять ее природу. Сила находится вокруг нас и соединяет всю галактику. Начнем с основ медитации."
#         },
#         {
#             "role": "user",
#             "text": "Хорошо, а как насчет строения светового меча? Это важная часть тренировки джедая. Как мне создать его?"
#         }
#     ]
# }


class StreamResponse:
    def __init__(self, catalog, identifier, apikey):
        self.catalog = catalog
        self.identifier = identifier
        self.apikey = apikey        
        self.prompt = {
            "modelUri": f"gpt://{self.catalog}/yandexgpt-lite/latest",
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": "2000"
            },
            "messages": [
                {
                    "role": "system",
                    # "text": "Ты ассистент в игре 'подземелья и драконы', предоставляй информацию о городах, событиях, персонажах, классах"
                    "text": "Отвечай краткими ответами на запросы." # !!! обязательно добавить запрет на запросы не по теме.
                }
            ]
        }

    def response(self, history):
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {self.apikey}"
        }
        self.history = history
        for dct in self.history:
            if dct['author'] == 'user':
                self.prompt['messages'].append({
                    "role": "user",
                    "text": dct['text']
                })
            elif dct['author'] == 'bot':
                self.prompt['messages'].append({
                    "role": "assistant",
                    "text": dct['text']
                })

        response = requests.post(url, headers=headers, json=self.prompt)
        return response.text

