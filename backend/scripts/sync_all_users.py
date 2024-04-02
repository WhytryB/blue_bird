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

session = requests.Session()
session.auth = HTTPBasicAuth("Федоров".encode(encoding='UTF-8',errors='strict'), BD_PASSWORD)

odata_url_phis_phase = f'{BD_HOST}Catalog_ФизическиеЛица?$format=json'


response = session.get(odata_url_phis_phase , headers={'Content-Type': 'application/json; charset=utf-8'})

def generate_random_username():
    # Генерация случайного логина из букв и цифр
    letters_and_digits = string.ascii_letters + string.digits
    random_username = ''.join(random.choice(letters_and_digits) for _ in range(8))
    return random_username

odata_url_phis_phase = f'{BD_HOST}Catalog_ПотребителиУслуг?$format=json'


response_uses = session.get(odata_url_phis_phase , headers={'Content-Type': 'application/json; charset=utf-8'})

if response_uses.status_code == 200:
    # Перебор данных и создание нового пользователя в Django
    odata_uses = response_uses.json()
    for entry in odata_uses.get('value', []):
        try:
            user_phone = entry.get('МобДляСайта')
            user_ref_key = entry.get('Ref_Key')
            user_name = entry.get('Description').split(' ')
            is_Folder = entry.get('IsFolder')
            username = generate_random_username()


            uses_user = False
            # for entry_uses in odata_uses.get('value', []):
            #     if entry_uses.get('ФизЛицо_Key') == user_ref_key:
            #         uses_user = True
            #         break
            print(user_name, username, uses_user,user_phone )

            url = f"{BD_HOST}Catalog_ПотребителиУслуг(guid'{user_ref_key}')?$format=json"

            try:
                exist_user = User.objects.get(ref_key=user_ref_key)
            except User.DoesNotExist:

                print(f"Create new user 3 {user_name}")
                if len(user_name) == 3:
                    user = User.objects.create_user(username=username, ref_key=user_ref_key,
                                                    first_name=user_name[1], last_name=user_name[0],
                                                    middle_name=user_name[2])


                else:
                    user = User.objects.create_user(username=username, ref_key=user_ref_key,
                                                    first_name=user_name[1], last_name=user_name[0])

                password = User.objects.make_random_password()
                user.set_password(password)
                user.save()

                response_user_patch = session.patch(url,
                                                    headers={'Content-Type': 'application/json; charset=utf-8'},
                                                    json={"Логин": user_phone, "Пароль": password})
            if len(user_phone) > 0:

                if exist_user:
                    try:
                        print(f"Update user {user_name}")
                        exist_user.username = user_phone
                        password = User.objects.make_random_password()
                        exist_user.set_password(password)
                        exist_user.save()

                        response_user_patch = session.patch(url,
                                                            headers={'Content-Type': 'application/json; charset=utf-8'},
                                                            json={"Логин": user_phone, "Пароль": password})
                    except Exception as e:
                        print(e)
                        print(f"Update user 2 {user_name}")
                        exist_user.username = username
                        password = User.objects.make_random_password()
                        exist_user.set_password(password)
                        exist_user.save()

                        response_user_patch = session.patch(url,
                                                            headers={'Content-Type': 'application/json; charset=utf-8'},
                                                            json={"Логин": username, "Пароль": password})
                else:
                    print(f"Create new user {user_name}")
                    if len(user_name) == 3:
                        user = User.objects.create_user(username=username, ref_key=user_ref_key,
                                                     first_name=user_name[1], last_name=user_name[0],
                                                     middle_name=user_name[2])


                    else:
                        user = User.objects.create_user(username=username, ref_key=user_ref_key,
                                                     first_name=user_name[1], last_name=user_name[0])

                    password = User.objects.make_random_password()
                    user.set_password(password)
                    user.save()



                    response_user_patch = session.patch(url,
                                                        headers={'Content-Type': 'application/json; charset=utf-8'},
                                                        json={"Логин": user_phone, "Пароль": password})
            else:
                if not exist_user:
                    print(f"Create new user 2 {user_name}")
                    if len(user_name) == 3:
                        user = User.objects.create_user(username=username, ref_key=user_ref_key,
                                                        first_name=user_name[1], last_name=user_name[0],
                                                        middle_name=user_name[2])


                    else:
                        user = User.objects.create_user(username=username, ref_key=user_ref_key,
                                                        first_name=user_name[1], last_name=user_name[0])

                    password = User.objects.make_random_password()
                    user.set_password(password)
                    user.save()

                    response_user_patch = session.patch(url,
                                                        headers={'Content-Type': 'application/json; charset=utf-8'},
                                                        json={"Логин": user_phone, "Пароль": password})



            # url_get = f"{BD_HOST}Catalog_ПотребителиУслуг?$format=json&$filter=Description eq '{entry.get('Description')}'"
            #
            # response_user_get = session.get(url_get, headers={'Content-Type': 'application/json; charset=utf-8'})
            #
            # if response_user_get.status_code == 200:
            #     response = response_user_get.json()
            #     if len(response.get('value', [])) > 0:
            #         print(f"Exists {len(response.get('value', []))}")
            #         lic_chet_code = response['value'][0]["Description"]
            #         lic_chet_code_main = response['value'][0]["Ref_Key"]




            print("Status", response_user_patch.status_code)
            #     else:
            #         with open('new_users.csv', mode='a', newline='') as csv_file:
            #             csv_writer = csv.writer(csv_file)
            #             csv_writer.writerow([entry.get('Description'), username, password, uses_user])
            #         print("Err")
            # else:
            #     with open('new_users.csv', mode='a', newline='') as csv_file:
            #         csv_writer = csv.writer(csv_file)
            #         csv_writer.writerow([entry.get('Description'), username, password, uses_user])
            #     print(f"Ошибка запроса: {response_user_get.status_code}")




        except Exception as e:
            with open('new_users.csv', mode='a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([entry.get('Description'), user_name])
            print(e)



    print("Скрипт выполнен успешно.")
else:
    print(f"Ошибка запроса: {response_uses.status_code}")
    print(response_uses.text)

