import requests
from requests.auth import HTTPBasicAuth
from requests.utils import quote
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

import os

import django
from django.conf import settings

settings_module = "backend.settings"  # Замените "your_project_name" на имя вашего Django проекта
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
django.setup()

from django.contrib.auth import get_user_model
# Получаем модель пользователя
User = get_user_model()
# Удаляем всех пользователей, кроме администраторов
non_admin_users = User.objects.filter(is_staff=False, is_superuser=False)
non_admin_users.delete()

print("Все пользователи, кроме администраторов, были удалены.")