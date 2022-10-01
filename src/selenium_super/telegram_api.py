import requests

class TelegramApi:
    def __init__(self, chat_id, bot_token) :
        self.chat_id = chat_id
        self.bot_token = bot_token

    def send_file(self, file_path, caption):
        try:
            files = {}
            files["document"] = open(file_path, "rb")
            url = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"
            return requests.get(url, params={"chat_id": self.chat_id,'caption':caption}, files=files)
        except Exception as e:
            print(e)
            return None

    def send_photo(self, file_path, caption):
        try:
            files = {}
            files["photo"] = open(file_path, "rb")
            url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
            return requests.get(url, params={"chat_id": self.chat_id,'caption':caption}, files=files)
        except Exception as e:
            print(e)
            return None
        
    def send_message(self, message):
        try:
            return requests.post(url=f'https://api.telegram.org/bot{self.bot_token}/sendMessage',
                   data={'chat_id': self.chat_id, 'text': message})
        except Exception as e:
            print(e)
            return None
        
   