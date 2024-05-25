import requests
from requests.auth import HTTPBasicAuth
import os, sys

current_script_directory = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.join(current_script_directory, '..')
sys.path.append(parent_directory)
from config import SMS_KEY, SMS_ID, SMS_SECRET

def send_sms(phone_number, message):
    try:
        url = f'https://api.mobizon.ua/service/Message/SendSMSMessage?apiKey={SMS_KEY}&recipient=' + phone_number + '&text=' + message
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False





class KyivstarAPI:
    def __init__(self):
        self.client_id = SMS_ID
        self.client_secret = SMS_SECRET
        self.token_url = "https://api-gateway.kyivstar.ua/idp/oauth2/token"
        self.sms_url = "https://api-gateway.kyivstar.ua/sandbox/rest/v1beta/sms"
        self.access_token = None

    def get_token(self):
        data = {
            'grant_type': 'client_credentials'
        }
        response = requests.post(self.token_url, data=data, auth=HTTPBasicAuth(self.client_id, self.client_secret))
        response.raise_for_status()  # Raise an error for bad status codes
        self.access_token = response.json().get('access_token')
        return self.access_token

    def send_sms(self, from_number, to_number, text):
        if not self.access_token:
            self.get_token()  # Ensure we have an access token

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        payload = {
            'from': from_number,
            'to': to_number,
            'text': text
        }
        response = requests.post(self.sms_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()



