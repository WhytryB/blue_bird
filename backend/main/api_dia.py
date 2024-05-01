import time

import requests
import os
import sys


current_script_directory = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.join(current_script_directory, '..')
sys.path.append(parent_directory)
from config import DIA_HOST, DIA_TOKEN
import hashlib
import base64
import uuid
import jinja2
import pdfkit




class DIA:
    def __init__(self):

        self.session_temp = requests.Session()
        self.session = requests.Session()
        self.headers_temp = {'Content-Type': 'application/json; charset=utf-8',
                             "Authorization": f"Basic {DIA_TOKEN}"}
        self.headers = {'Content-Type': 'application/json; charset=utf-8'}


    def handle_errors(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Error: {str(e)}")
                return None

        return wrapper


    def perform_resopnse_api(self, response):
        if response.status_code == 200:
            response = response.json()
            return response
        elif response.status_code == 404 or response.status_code == 401:
            token = self.get_dia_token()
            self.headers.update({"Authorization": f"Bearer {token}"})
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None



    @handle_errors
    def get_dia_token(self):
        response = self.session_temp.get(f"{DIA_HOST}/api/v1/auth/acquirer/bluebird_test_token_pgl090",  headers=self.headers_temp)
        response = self.perform_resopnse_api(response)
        return response['token']


    def check_headers(self):
        if self.headers == {'Content-Type': 'application/json; charset=utf-8'}:
            token = self.get_dia_token()
            self.headers.update({"Authorization": f"Bearer {token}"})


    @handle_errors
    def create_dia_file(self, poll, file_name):

        # Load the template
        env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))
        template = env.get_template("main/dia_template.html")

        html_out = template.render(head_text=poll['head_text'],
                                   question=poll['question'],
                                   results=poll['results'],
                                   user_name=poll['user_name'],
                                   user_answer=poll['user_answer']
                                   )
        options = {
            "enable-local-file-access": None
        }
        file_ = open(f"main/media/temp/output_{file_name}.html", 'wb')
        file_.write(html_out.encode("utf-8"))
        file_.close()
        if os.path.exists(f"main/media/temp/output_{file_name}.html"):
            print("File created")
        else:
            print("Ошибка: Файл не был создан.")
            time.sleep(3)

        # write the pdf to file
        pdfkit.from_string(html_out, output_path=f"main/media/temp/{file_name}", options=options)


    @handle_errors
    def calculate_file_hash(self, file_path):
        # Открываем файл для чтения в бинарном режиме
        with open(f"main/media/temp/{file_path}", "rb") as file:
            # Вычисляем хеш файла с использованием SHA256
            file_hash = hashlib.sha256(file.read()).digest()
            # Кодируем хеш в base64 и возвращаем как строку
            return base64.b64encode(file_hash).decode()


    @handle_errors
    def get_branches(self):
        self.check_headers()

        response = self.session.get(f"{DIA_HOST}/api/v2/acquirers/branches", headers=self.headers)
        response = self.perform_resopnse_api(response)
        return response

    @handle_errors
    def post_offer(self, branch, name):
        data = {
            "name": name,
            "scopes": {
                "diiaId": ["hashedFilesSigning"]
            }
        }
        response = self.session.post(f"{DIA_HOST}/api/v1/acquirers/branch/{branch}/offer",
                                    headers=self.headers,
                                    json=data)
        response = self.perform_resopnse_api(response)
        return response

    @handle_errors
    def hash_request_id(self):

        request_id = uuid.uuid4()
        request_id_str = str(request_id)

        hash_object = hashlib.sha256(request_id_str.encode())
        hash_value = hash_object.digest()

        return base64.b64encode(hash_value).decode()

    @handle_errors
    def get_offer(self, branch):
        response = self.session.get(f"{DIA_HOST}/api/v1/acquirers/branch/{branch}/offers",
                                    headers=self.headers)
        response = self.perform_resopnse_api(response)
        return response


    @handle_errors
    def post_dynamic(self, branch, offer_id, requestId, file_name, file_hash):
        data = {
          "offerId": offer_id,
          "returnLink": "https://ptah.osbb.house/vote/",
          "signAlgo": "ECDSA",
          "requestId": requestId,
          "data": {
            "hashedFilesSigning": {
              "hashedFiles": [
                {
                  "fileName": file_name,
                  "fileHash": file_hash
                }
              ]
            }
          }

        }
        response = self.session.post(f"{DIA_HOST}/api/v2/acquirers/branch/{branch}/offer-request/dynamic",
                                     headers=self.headers,
                                     json=data)
        response = self.perform_resopnse_api(response)
        return response

