import requests
import os, sys

current_script_directory = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.join(current_script_directory, '..')
sys.path.append(parent_directory)
from config import SMS_KEY

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