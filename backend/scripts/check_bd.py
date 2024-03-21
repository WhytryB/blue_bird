import requests
from requests.auth import HTTPBasicAuth
import csv
import os
import sys
import string
import uuid
import random

# Добавляем путь к родительскому каталогу в sys.path
current_script_directory = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.join(current_script_directory, '..')
sys.path.append(parent_directory)
from config import BD_HOST, BD_LOGIN, BD_PASSWORD


import django
from django.conf import settings

settings_module = "backend.settings"  # Замените "your_project_name" на имя вашего Django проекта
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

print(BD_PASSWORD, BD_LOGIN.encode(encoding='UTF-8',errors='strict'), BD_HOST, BD_LOGIN, BD_PASSWORD)

session = requests.Session()
session.auth = HTTPBasicAuth("Федоров".encode(encoding='UTF-8',errors='strict'), BD_PASSWORD)

odata_url_phis_phase = f'{BD_HOST}Catalog_ФизическиеЛица?$format=json'


response = session.get(odata_url_phis_phase , headers={'Content-Type': 'application/json; charset=utf-8'})


print(BD_PASSWORD, BD_LOGIN.encode(encoding='UTF-8',errors='strict'), BD_HOST, BD_LOGIN, BD_PASSWORD, response.status_code, response.text)