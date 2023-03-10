import requests
import yaml
import re


class Translator:
    def __init__(self):
        self.url = "https://google-translate1.p.rapidapi.com/language/translate/v2"
        self.headers = {
            "content-type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "application/gzip",
            "X-RapidAPI-Key": None,
            "X-RapidAPI-Host": "google-translate1.p.rapidapi.com"
        }

        self._get_api_key()

    def _get_api_key(self):
        # Read YAML file
        with open("config.yaml", 'r') as stream:
            config_data = yaml.safe_load(stream)
            self.headers['X-RapidAPI-Key'] = config_data['API_KEY']

    def make_translation(self, source_language: str = 'en', target_language: str = 'hi', texts: list = []) -> str:
        payload = f"source={source_language}&target={target_language}"
        for text in texts:
            clean_text = re.sub(r'[^a-zA-Z0-9 \._-]', '', text)
            payload += f'&q={clean_text}'

        response = requests.request("POST", self.url, data=payload, headers=self.headers)
        if response.status_code == 200:
            return response.json()['data']['translations']
        else:
            print(response.json())


if __name__ == "__main__":
    translator = Translator()
    t = translator.make_translation(texts=["Hola Mundo", "Hola Mundo"])
    print(t)
