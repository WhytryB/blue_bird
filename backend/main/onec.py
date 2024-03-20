import requests
from requests.auth import HTTPBasicAuth
import os
import sys
import string
import uuid
import random


current_script_directory = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.join(current_script_directory, '..')
sys.path.append(parent_directory)
from config import BD_HOST, BD_LOGIN, BD_PASSWORD, BD_1CAPI


import django
from django.conf import settings

settings_module = "backend.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
django.setup()

from django.contrib.auth import get_user_model





class OSBB:
    def __init__(self):

        self.user_model = get_user_model()
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(BD_LOGIN.encode(encoding='UTF-8',errors='strict'), BD_PASSWORD)
        self.headers = {'Content-Type': 'application/json; charset=utf-8'}
        self.headers_patch = {'Content-Type': 'application/json; charset=utf-8'}


    def handle_errors(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Error: {str(e)}")
                return None

        return wrapper

    def perform_resopnse_odata(self, response):
        if response.status_code == 200:
            response = response.json()
            if len(response.get('value', [])) > 0:
                print(f"Found {len(response.get('value', []))}")
                return response.get('value', [])
            else:
                print(f"Not found")
                return None
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def perform_resopnse_api(self, response):
        if response.status_code == 200:
            response = response.json()
            return response
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def perform_resopnse_patch_odata(self, response):
        if response.status_code == 200:
            response = response.json()
            return response
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None


    @handle_errors
    def get_users_phis(self):
        response = self.session.get(f'{BD_HOST}Catalog_ФизическиеЛица?$format=json', headers=self.headers)
        response = self.perform_resopnse_odata(response)
        return response

    @handle_errors
    def get_lic_odata(self):
        response = self.session.get(f'{BD_HOST}Catalog_ЛицевыеСчета?$format=json', headers=self.headers)
        response = self.perform_resopnse_odata(response)
        return (response)


    @handle_errors
    def get_users(self):
        response = self.session.get(f'{BD_HOST}Catalog_ПотребителиУслуг?$format=json', headers=self.headers)
        response = self.perform_resopnse_odata(response)
        return response

    @handle_errors
    def get_user_by_desc(self, desc):
        response = self.session.get(f"{BD_HOST}Catalog_ПотребителиУслуг?$format=json&$filter=Description eq '{desc}'",
                                    headers=self.headers)
        response = self.perform_resopnse_odata(response)
        return response[0]


    @handle_errors
    def get_user_by_username(self, desc):
        response = self.session.get(f"{BD_HOST}Catalog_ПотребителиУслуг?$format=json&$filter=Логин eq '{desc}'",
                                    headers=self.headers)
        response = self.perform_resopnse_odata(response)
        return response[0]

    @handle_errors
    def patch_user(self, guid, data):
        response = self.session.patch(f"{BD_HOST}Catalog_ПотребителиУслуг(guid'{guid}')?$format=json",
                                    headers=self.headers,
                                    json=data)
        response = self.perform_resopnse_patch_odata(response)
        return response

    @handle_errors
    def patch_vote(self, guid, data):
        response = self.session.patch(f"{BD_HOST}Document_Голосование(guid'{guid}')?$format=json",
                                      headers=self.headers,
                                      json=data)
        response = self.perform_resopnse_patch_odata(response)
        return response

    @handle_errors
    def get_lich_user(self, username):
        response = self.session.get(f"{BD_1CAPI}Инфо?name={username}",
                                    headers=self.headers)
        response = self.perform_resopnse_api(response)
        return response

    @handle_errors
    def get_ostatok_user(self, code):
        response = self.session.get(f"{BD_1CAPI}Остаток?code={code}",
                                    headers=self.headers)
        response = self.perform_resopnse_api(response)
        return response

    @handle_errors
    def get_raschet_user(self, code):
        response = self.session.get(f"{BD_1CAPI}Расчёт?code={code}",
                                    headers=self.headers)
        response = self.perform_resopnse_api(response)
        return response


    @handle_errors
    def get_priboru_user(self, code):
        response = self.session.get(f"{BD_1CAPI}Услуги?code={code}",
                                    headers=self.headers)
        response = self.perform_resopnse_api(response)
        return response


    @handle_errors
    def get_unique_priboru_user(self, code):
        response = self.session.get(f"{BD_1CAPI}Приборы?code={code}",
                                    headers=self.headers)
        response = self.perform_resopnse_api(response)
        return response


    @handle_errors
    def post_schetchik(self, data):
        response = self.session.post(f"{BD_1CAPI}ВводАПИ", json=data, headers=self.headers)
        response = self.perform_resopnse_api(response)
        return response


    @handle_errors
    def get_cars_user(self, code):
        response = self.session.get(f"{BD_1CAPI}Машины?code={code}", headers=self.headers)
        response = self.perform_resopnse_api(response)
        return response

    @handle_errors
    def get_votes_result(self):
        response = self.session.get(f"{BD_1CAPI}Голосование", headers=self.headers)
        response = self.perform_resopnse_api(response)
        return response

    @handle_errors
    def post_cars(self, data):
        response = self.session.post(f"{BD_1CAPI}Машины", json=data, headers=self.headers)
        response = self.perform_resopnse_api(response)
        return response

    @handle_errors
    def delete_cars(self, guid):
        response = self.session.delete(f"{BD_HOST}Document_ИзменениеЛицевогоСчета(guid'{guid}')?$format=json",
                                      headers=self.headers)
        response = self.perform_resopnse_patch_odata(response)
        return response

    @handle_errors
    def get_cars(self):
        response = self.session.get(f"{BD_HOST}Document_ИзменениеЛицевогоСчета?$format=json&$expand=*",
                                       headers=self.headers)
        response = self.perform_resopnse_odata(response)
        return response


    @handle_errors
    def get_votes(self):
        response = self.session.get(f"{BD_HOST}Document_ИнформационныйЛистДляГолосования?$format=json&$expand=*",
                                       headers=self.headers)
        response = self.perform_resopnse_odata(response)
        return response

    @handle_errors
    def get_votes_doc(self):
        response = self.session.get(f"{BD_HOST}Document_Голосование?$format=json&$expand=*",
                                       headers=self.headers)
        response = self.perform_resopnse_odata(response)
        return response



