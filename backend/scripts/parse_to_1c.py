import argparse
import time
import re
from selenium import webdriver
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import string
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse  import quote_plus
import csv
import os
import sys
import string
import uuid
import random
from urllib.parse import quote
from datetime import datetime
from operator import itemgetter
import itertools


# Добавляем путь к родительскому каталогу в sys.path
current_script_directory = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.join(current_script_directory, '..')
sys.path.append(parent_directory)
from config import BD_HOST, BD_LOGIN, BD_PASSWORD




const_objects_counts = "https://admin.asn.od.ua/frontend/frontend.php?storevars=1&form_id=srkf_form&uriid=0&do_system=1&mod=ls&but_name=&page=&pagesize=&pagesmax=&do_dom=1&dom_default=523&dom=523&ugroup=1097&ugroup_option=0&lsstr=%D0%BC%D0%B0%D1%80%D1%96%D0%BD%D0%B0&is_office=0&lsid=12182&type_id_default=203&type_id=203&type_id_t=0&avars%5B%5D=do_kv_num&avars%5B%5D=kv_num_type&avars%5B%5D=kv_num_t&avars%5B%5D=kv_num&kv_num=139&kv_num_t=1&date_do=202312&is_lgota=0&is_income=1&debt_summ_p=1&debt_summ_t=1&debt_summ=30000&ls_opt=summ&do_xvar=1&xvar=account.contacts.persona_phone&xvar_option=0&do_yvar=1&yvar=account.contacts.%40%40persona_email&yvar_option=0&sort=0&sbtn0=%D0%9F%D0%BE%D0%B8%D1%81%D0%BA&myname=lsl&do_select=1&do_form=1&do_create=1"
Error_list = []
const_objects_scheta = "https://admin.asn.od.ua/frontend/frontend.php?storevars=1&form_id=srkf_form&uriid=0&do_system=1&mod=ls&but_name=&page=&pagesize=&pagesmax=&do_dom=1&dom_default=523&dom=523&ugroup=1097&ugroup_option=0&lsstr=%D0%BC%D0%B0%D1%80%D1%96%D0%BD%D0%B0&is_office=0&lsid=12182&type_id_default=203&type_id=203&type_id_t=0&avars%5B%5D=do_kv_num&avars%5B%5D=kv_num_type&avars%5B%5D=kv_num_t&avars%5B%5D=kv_num&kv_num=117&kv_num_t=1&date_do=202401&is_lgota=0&is_income=1&debt_summ_p=1&debt_summ_t=1&debt_summ=5000&ls_opt=summ&xvar=account.%40objects.object_name&xvar_option=0&yvar=account.contacts.%40%40persona_email&yvar_option=0&sort=0&sbtn0=%D0%9F%D0%BE%D0%B8%D1%81%D0%BA&myname=lsl&do_select=1&do_form=1&do_create=1"
const_schetchiki = "https://admin.asn.od.ua/frontend/frontend.php?storevars=1&form_id=srkf_form&uriid=0&do_system=1&mod=cnts&but_name=&page=&pagesize=&pagesmax=&do_dom=1&dom_default=523&dom=523&ugroup=1097&ugroup_option=0&lsid=12182&type_id_default=203&type_id=203&type_id_t=0&avars%5B%5D=do_kv_num&avars%5B%5D=kv_num_type&avars%5B%5D=kv_num_t&avars%5B%5D=kv_num&kv_num=78&kv_num_t=1&counter_type=ot&ser_number=2676037&ser_number_t=1&edizm=gcal&cnts_opt=1&cnts_opts=1&cnts_err=0&sbtn0=%D0%9F%D0%BE%D0%B8%D1%81%D0%BA&myname=cntsl&do_select=1&do_form=1&do_create=1"

def parse_personal_info(driver, session):
    driver.get(const_objects_counts)
    time.sleep(1)
    # Находим все элементы <tr> с помощью XPath
    rows = driver.find_elements(By.XPATH, "//tr[contains(@id, 'row_')]")

    # Перебираем каждый элемент <tr>
    for row in rows[1:]:
        # Извлекаем имя из элемента <b> внутри текущего <tr>
        try:
            name_element = row.find_element(By.XPATH, ".//b")
            name = name_element.text.strip()
            search_name = name.replace("'", "\'")

            # Извлекаем контакты (почта и телефон) из элементов <td> внутри текущего <tr>
            contact_elements = row.find_elements(By.XPATH, ".//td[@class='td1' and not(@align='center')]/input[not (@type='hidden') and not (@type='button')]")
            contacts = [contact.get_attribute("value").strip() for contact in contact_elements]


            if "ТОВ" not in name and "ПП" not in name and "-Інвест" not in name and '5' not in name:
                    # Выводим результаты
                    print("Имя:", name)
                    print("Контакты:", contacts)
                    print("=" * 50)

                    odata_url = f'{BD_HOST}Catalog_ПотребителиУслуг?$filter=Description eq \'{search_name}\'&$format=json'


                    response = session.get(odata_url , headers={'Content-Type': 'application/json; charset=utf-8'})
                    if response.status_code == 200:
                        response = response.json()
                        print(response)
                        if len(response.get('value', [])) > 0:
                            temp_ur = response['value'][0]['Ref_Key']
                            odata_url_patch = f'{BD_HOST}Catalog_ПотребителиУслуг(guid\'{temp_ur}\')?$format=json'
                            print(odata_url_patch)
                            data = {"МобДляСайта": contacts[0], "ЕлектроннаяПочта": contacts[1]}
#                             response_patch = session.patch(odata_url_patch, headers={'Content-Type': 'application/json; charset=utf-8'}, json=data)
#                             print(response_patch.status_code, response_patch.json())
                        else:
                            print('post')
                            Error_list.append({"name": name, "response": response})
#                             odata_url_patch = f'{BD_HOST}Catalog_ПотребителиУслуг?$format=json'
#                             odata_url_post_phis = f'{BD_HOST}Catalog_ФизическиеЛица?$format=json'
#                             odata_url_patch_phis = f'{BD_HOST}Catalog_ФизическиеЛица?$filter=Description eq \'{search_name}\'&$format=json'
#                             response = session.get(odata_url_patch_phis , headers={'Content-Type': 'application/json; charset=utf-8'})
#                             response = response.json()
#
#                             if len(response.get('value', [])) > 0:
#                                 ref_key = response['value'][0]["Ref_Key"]
#                                 data = {"МобДляСайта": contacts[0],
#                                         "ЕлектроннаяПочта": contacts[1],
#                                         "Description": name,
#                                         "ФизЛицо_Key": ref_key,
#                                         "ЮрФизЛицо": "ФизЛицо",
#                                         "ОбновитьПароль": False,
#                                         }
#                                 response_patch = session.post(odata_url_patch, headers={'Content-Type': 'application/json; charset=utf-8'}, json=data)
#                                 print(response_patch.status_code, response_patch.json())
#
#                             else:
#                                  data = {"Parent_Key": "10ca2f4a-898e-11ee-a666-7cfe9013d29e",
#                                         "IsFolder": False,
#                                         "Description": name,
#                                  }
#                                  response_post = session.post(odata_url_post_phis, headers={'Content-Type': 'application/json; charset=utf-8'}, json=data)
#                                  ref_key = response_post.json()["Ref_Key"]
#                                  data = {"МобДляСайта": contacts[0],
#                                          "ЕлектроннаяПочта": contacts[1],
#                                          "Description": name,
#                                          "ФизЛицо_Key": ref_key,
#                                          "ЮрФизЛицо": "ФизЛицо",
#                                          "ОбновитьПароль": False,
#                                          }
#                                  response_patch = session.post(odata_url_patch, headers={'Content-Type': 'application/json; charset=utf-8'}, json=data)
#                                  print(response_patch.status_code, response_patch.json())
#                                  print('Nonee')

#                             print(odata_url_patch)
#                             data = {"МобДляСайта": contacts[0],
#                             "ЕлектроннаяПочта": contacts[1],
#                             "Description": name,
#                             "ФизЛицо_Key": "",
#                             "ЮрФизЛицо": "ФизЛицо",
#                             "ОбновитьПароль": False,
#                             }
#                             response_patch = session.post(odata_url_patch, headers={'Content-Type': 'application/json; charset=utf-8'}, json=data)
#                             print(response_patch.status_code, response_patch.json())

                    else:
                        Error_list.append({"name": name, "response": response})
        except Exception as e:
            print(e)
            Error_list.append({"name": name, "response": response})
    print("end", Error_list)


def process_string(input_string):
    # Регулярное выражение для различных форматов


    keywords = ["мм", "кл", "кв", "оф"]
    if 'мм' in input_string:

        input_string = input_string.replace('мм.', 'м.м').split()

        input_string = input_string[0] + ' № ' + input_string[-1]
        input_string = input_string.replace('-н', '')

    elif 'кл' in input_string:
        match = re.search(r'\d+', input_string).group()
        input_string = input_string.split()

        if len(match) == 1:
            space = '   '
        elif len(match) == 2:
            space = '  '
        else:
            space = ' '
        input_string = "кл" + ' №' + space + input_string[-1]
    elif 'к' in input_string and '-н' in input_string:

        match = re.search(r'\d+', input_string).group()
        if len(match) == 1:
            space = '   '
        elif len(match) == 2:
            space = '  '
        else:
            space = ' '
        input_string = "кл №" + space + str(match)
    elif 'кв' in input_string:
        match = re.search(r'\d+', input_string).group()
        if len(match) == 1:
            space = '   '
        elif len(match) == 2:
            space = '  '
        else:
            space = ' '
        input_string = input_string.replace('-', '').split()
        input_string = input_string[0] + ' №' + space + input_string[-1]
    elif 'оф' in input_string:
        match = re.search(r'\d+', input_string).group()
        if len(match) == 1:
            space = '   '
        elif len(match) == 2:
            space = '  '
        else:
            space = ' '
        input_string = input_string.replace('.', '').split()
        input_string = input_string[0] + ' №' + space + input_string[-1]

    return input_string


def process_string_type(input_string, type):
    # Регулярное выражение для различных форматов
    if type == "203":
        input_string = input_string.replace('-', '').strip()
        match = re.search(r'\d+', input_string).group()
        if len(match) == 1:
            space = '   '
        elif len(match) == 2:
            space = '  '
        else:
            space = ' '

        input_string = "кв."+ ' №' + space + match

        return input_string
    elif type == "204":
        match = re.search(r'\d+', input_string).group()
        input_string = 'м.м № ' + match

    elif type == "205":
        match = re.search(r'\d+', input_string).group()
        if len(match) == 1:
            space = '   '
        elif len(match) == 2:
            space = '  '
        else:
            space = ' '
        input_string = "оф" + ' №' + space + match

    elif type == "209":
        match = re.search(r'\d+', input_string).group()
        input_string = input_string.split()

        if len(match) == 1:
            space = '   '
        elif len(match) == 2:
            space = '  '
        else:
            space = ' '
        input_string = "кл" + ' №' + space + match


    return input_string




def process_string_kv(input_string):
    # Регулярное выражение для различных форматов


    input_string = input_string.replace('-', '').strip()
    match = re.search(r'\d+', input_string).group()
    if len(match) == 1:
        space = '   '
    elif len(match) == 2:
        space = '  '
    else:
        space = ' '

    input_string = "кв."+ ' №' + space + input_string

    return input_string




def parse_scheta(driver, session):
    driver.get(const_objects_scheta)
    time.sleep(1)
    # Находим все элементы <tr> с помощью XPath
    rows = driver.find_elements(By.XPATH, "//tr[contains(@id, 'row_')]")

    # Перебираем каждый элемент <tr>
    for row in rows[1:]:
        # Извлекаем имя из элемента <b> внутри текущего <tr>
        try:
            name_element = row.find_element(By.XPATH, ".//td[@valign='top']/b")
            name = name_element.text.strip()
            search_name = name

            # Извлекаем контакты (почта и телефон) из элементов <td> внутри текущего <tr>
            id_elements = row.find_elements(By.XPATH, ".//td[@id='hhth']/input")
            ids = [idss.get_attribute("value").strip() for idss in id_elements]


            objects_elements = row.find_elements(By.XPATH, ".//tr[@style='background-color:#ffffd0;' or @style='background-color:#D0ffD0;'] /td[@style='break-inside:avoid;']")
            objs = [obj.text.strip() for obj in objects_elements]


            if "ТОВ" not in name and "ПП" not in name and "-Інвест" not in name:
                    # Выводим результаты
                    if "Ремінна Віра Миколаївна" == name:
                        name = "Ремінна Віра Миколаевна"
                    elif 'Осадча Наталя Іванівна,' == name:
                        name = "Осадча Наталія Іванівна"
                    elif 'Осадча Наталя Іванівна' == name:
                        name = "Осадча Наталія Іванівна"
                    print("Имя:", name)
                    print("Id:", ids)
                    print("Objects:", objs)
                    print("=" * 50)

                    for obj in objs:
                        result = process_string(obj)
                        print(result)
                        odata_url = f'{BD_HOST}Catalog_ЛицевыеСчета?$format=json&$expand=ОбъектЛицевогоСчета&$filter=ОбъектЛицевогоСчета/Description eq \'{result}\''
                        print(odata_url)
                        response = session.get(odata_url , headers={'Content-Type': 'application/json; charset=utf-8'})
#                         print(response.status_code, response.json())
                        if response.status_code == 200:
                            response = response.json()
                            if len(response.get('value', [])) > 0:
                                print(f"Exists {len(response.get('value', []))}")
                            else:

                                odata_2_url = f'{BD_HOST}Catalog_ОбъектыЛицевыхСчетов?$format=json&$filter=Description eq \'{result}\''
                                response = session.get(odata_2_url , headers={'Content-Type': 'application/json; charset=utf-8'})

                                if response.status_code == 200:
                                    response = response.json()
                                    if len(response.get('value', [])) > 0:
                                        ref_key = response['value'][0]["Ref_Key"]


                                        data = {"КодЗдания": "000000001", "RefObj": result, "ОрганизацияКод": "00-000001",  'Owner': name, 'Description': ids[0]}
                                        response = session.post('http://osbb.tais-dtb.com:8280/OSBB/hs/API/Лицевой' , headers={'Content-Type': 'application/json; charset=utf-8'}, json=data)

                                        if response.status_code != 200:
                                            print(response.status_code, response.json())
                                            breakpoint()





#                                         data = {"Owner_Key": "dc454ae6-83f2-11ee-a666-7cfe9013d29e", "Description": str(ids[0]), "ОбъектЛицевогоСчета_Key": ref_key}
#                                         odata_post_url = f'{BD_HOST}Catalog_ЛицевыеСчета?$format=json'
#                                         response_patch = session.post(odata_post_url, headers={'Content-Type': 'application/json; charset=utf-8'}, json=data)
#                                         print(response_patch.status_code, response_patch.json())
#                                         if response_patch.status_code == 201:
#                                             ref_key = response_patch.json()["Ref_Key"]
#                                             current_time = datetime.now()
#                                             formatted_time = current_time.strftime("%Y-%m-%dT%H:%M:%S")
#                                             data = {"DeletionMark": False, "Комментарий": "", "КоличествоПроживающих": 0, "КоличествоПрописанных": 0,  "ДатаПоследнегоИзменения": formatted_time,  "ДополнительныеРеквизиты": [], "Date": formatted_time, "Posted": True,  "Number": "00000000226", "Owner_Key": "dc454ae6-83f2-11ee-a666-7cfe9013d29e", "Здание_Key": "dc454ae6-83f2-11ee-a666-7cfe9013d29e", "Организация_Key": "cf0e4aa9-83ea-11ee-a666-7cfe9013d29e",   "Автор_Key": "cf7d63a7-8850-11ee-a666-7cfe9013d29e", "ОтветственныйВладелец_Key": "08308b1c-b06f-11ee-a67f-7cfe9013d29e", "ЛицевойСчет_Key": ref_key}
#                                             odata_post_url = f'{BD_HOST}Document_ОткрытиеЛицевогоСчета?$format=json'
#
#                                             response_post = session.post(odata_post_url, headers={'Content-Type': 'application/json; charset=utf-8'}, json=data)
#                                             ref_key2 = response_post.json()["Ref_Key"]
#                                             data2 = {"Recorder": ref_key2, "Recorder_Type": "StandardODATA.Document_ИзменениеЛицевогоСчета", "RecordSet" : str([{"Period": formatted_time, "LineNumber": "1", "Active": True, "ЛицевойСчет_Key": ref_key, "ОтветственныйВладелец_Key": "08308b1c-b06f-11ee-a67f-7cfe9013d29e"}]) }
#
#                                             odata_post2_url = f'{BD_HOST}InformationRegister_ОтветственныйВладелецЛицевогоСчета?$format=json'
#                                             response2_post = session.post(odata_post2_url, headers={'Content-Type': 'application/json; charset=utf-8'}, json=data2)



                                    else:
                                        print('Dont exist')
                                else:
                                    breakpoint()
                        else:
                            breakpoint()




        except Exception as e:
            print(e)
            breakpoint()
            Error_list.append({"name": name, "response": response})
    print("end", Error_list)



def perform_data(data):
    input_date = datetime.strptime(data, "%d.%m.%Y")

    # Преобразование объекта datetime в новый формат строки
    output_date_string = input_date.strftime("%Y%m%d")

    return output_date_string



def parse_schetchiki(driver, session):
    driver.get(const_schetchiki)
    time.sleep(1)
    # Находим все элементы <tr> с помощью XPath
    rows = driver.find_elements(By.XPATH, "//tr[contains(@id, 'row_')]")
    data = []
    # Перебираем каждый элемент <tr>
    for row in rows[1:]:
        # Извлекаем имя из элемента <b> внутри текущего <tr>
        try:
            name_element = row.find_element(By.XPATH, ".//td[2]")
            name = name_element.text.strip()
            search_name = name

            type_element = row.find_element(By.XPATH, ".//td[4]").text.strip()
            kv_number = row.find_element(By.XPATH, ".//td[3]").text.strip()
            ser_number_element = row.find_element(By.XPATH, ".//td[8]").text.strip()
            active_element = row.find_element(By.XPATH, ".//td[10]").text.strip()
            start_poz_element = row.find_element(By.XPATH, ".//td[11]").text.strip()
            edin_element = row.find_element(By.XPATH, ".//td[12]").text.strip()
            karta_elem = row.find_element(By.XPATH, ".//td[13]").text.strip()
            is_pokazania = row.find_element(By.XPATH, ".//td[7]").text.strip()

            card_element = row.find_element(By.XPATH, ".//td[13]/input")

            # Получение значения атрибута onclick
            onclick_value = card_element.get_attribute("onclick")

            uid_match = re.search(r"uid:(\d+)", onclick_value)
            cid_match = re.search(r"cid:(\d+)", onclick_value)

            # Значения uid и cid
            uid = uid_match.group(1) if uid_match else None
            cid = cid_match.group(1) if cid_match else None

            if "ТОВ" not in name and "ПП" not in name and "-Інвест" not in name and active_element == "Открыто" and is_pokazania != "НЕТ":
                    # Выводим результаты
                    print("Имя:", name)
                    print("Type:", type_element)
                    print("Ser_number:", ser_number_element)
                    print("Active:", active_element)
                    print("Start_poz:", start_poz_element)
                    print("Edin:", edin_element)
                    print("Karta:", karta_elem)
                    print("uid", uid)
                    print("cid", cid)

                    print("=" * 50)


                    odata_url = f'{BD_HOST}Catalog_ПриборыУчета?$format=json&$filter=ЗаводскойНомер eq \'{ser_number_element}\''
                    print(odata_url)
                    response = session.get(odata_url , headers={'Content-Type': 'application/json; charset=utf-8'})
#                         print(response.status_code, response.json())
                    if response.status_code == 200:
                        response = response.json()
                        if len(response.get('value', [])) > 0:
                            print("Def")
                        else:


                            yslyga_code = None
                            if type_element == "Счетчик электрический":
                                yslyga_code = "000000016"
                            elif type_element == "Счетчик холодной воды":
                                yslyga_code = "000000048"
                            elif type_element == "Счетчик тепла отопления":
                                yslyga_code = "000000009"
                            elif type_element == "Счетчик горячей воды":
                                yslyga_code = "000000044"

                            izmerenie_code = None
                            if edin_element == "МВт" or edin_element == "ГДж" or edin_element == "Гкал":
                                izmerenie_code = "Гкал"
                            elif edin_element == "КВт/час":
                                izmerenie_code = "кВт·год"
                            elif edin_element == "куб.м.":
                                izmerenie_code = "м3"
                            elif edin_element == "КВт(Тепло)":
                                izmerenie_code = "кВт"


                            if is_pokazania != "НЕТ":
                                pokazania_list = []
                                try:

                                    pokazania_url = f"https://admin.asn.od.ua/frontend/frontend.php?myname=cvl&uid={uid}&cid={cid}&op=form&do_form=1&parent_win_id=winp_17&win_id=winp_18"


                                    # Открытие новой вкладки
                                    driver.execute_script("window.open('https://www.example.com', '_blank');")

                                    # Получение списка идентификаторов вкладок
                                    handles = driver.window_handles

                                    # Переключение на новую вкладку
                                    driver.switch_to.window(handles[1])

                                    # Работа с новой вкладкой (например, выполнение каких-то действий)

                                    driver.get(pokazania_url)

                                    pokaz_rows = driver.find_elements(By.XPATH, "//tr")

                                    # Перебираем каждый элемент <tr>
                                    for pokaz_row in pokaz_rows[1:]:
                                        pokaz_data = pokaz_row.find_element(By.XPATH, ".//td[1]").text.strip()
                                        pokaz_prev = pokaz_row.find_element(By.XPATH, ".//td[2]").text.strip()
                                        pokaz_new = pokaz_row.find_element(By.XPATH, ".//td[3]").text.strip()

                                        print(pokaz_data, pokaz_prev, pokaz_new)
                                    print("-" * 50)


                                    # Закрытие новой вкладки

                                    совпадение = re.search(r'\d{2}.\d{2}.\d{4} \d{2}:\d{2}', pokaz_data)
                                    строкаДатаВремя = совпадение.group(0)

                                    # Преобразуем строку даты и времени в формате строки
                                    толькоДата = datetime.strptime(строкаДатаВремя, '%d.%m.%Y %H:%M').strftime('%d.%m.%Y')



                                    pokazania_list.append({"ДатаУстановки": perform_data(толькоДата), "НачальноеПоказание": pokaz_new})
                                    driver.close()

                                    # Переключение обратно на первую вкладку (если необходимо)
                                    driver.switch_to.window(handles[0])
                                except Exception as e:
                                    breakpoint()
                                    print(e)

                                odata_url = f'{BD_HOST}Catalog_ЛицевыеСчета?$format=json&$expand=ОбъектЛицевогоСчета&$filter=ОбъектЛицевогоСчета/Description eq \'{process_string_kv(kv_number)}\''
                                print(odata_url)
                                response = session.get(odata_url , headers={'Content-Type': 'application/json; charset=utf-8'})
                                lic_chet = ""
                                if response.status_code == 200:
                                    response = response.json()
                                    if len(response.get('value', [])) > 0:
                                        print(f"Exists {len(response.get('value', []))}")
                                        lic_chet = response['value'][0]["Description"]

                                data = {"КодУслуги": yslyga_code, "КодИзмерения": izmerenie_code,"КодЗдания": "000000001", "КодЗаводской": ser_number_element,  "ОрганизацияКод": "00-000001", "ОбъектУстановки": lic_chet, "СтрокаДата": "20230701"  ,"ПриборыУчета": pokazania_list}

                                response = session.post('http://osbb.tais-dtb.com:8280/OSBB/hs/API/Счётчик' , headers={'Content-Type': 'application/json; charset=utf-8'}, json=data)
                                if response.status_code != 200:
                                    print(response.status_code, response.json())
                                    breakpoint()
                                else:
                                    print(f"Прибор учета {ser_number_element} успешно добавлен для лицевого счета {lic_chet}")
                                    print("Exist")
                            else:
                                print('No pokazania')






                    else:
                        Error_list.append({"name": name, "response": response})
                        breakpoint()


        except Exception as e:
            print(e)
            breakpoint()
            Error_list.append({"name": name, "response": response})


def parse_schetchiki_doc(driver, session):



    driver.get(const_schetchiki)
    time.sleep(1)
    # Находим все элементы <tr> с помощью XPath
    rows = driver.find_elements(By.XPATH, "//tr[contains(@id, 'row_')]")
    data = []
    # Перебираем каждый элемент <tr>
    for row in rows[1:]:
        # Извлекаем имя из элемента <b> внутри текущего <tr>
        try:
            name_element = row.find_element(By.XPATH, ".//td[2]")
            name = name_element.text.strip()
            search_name = name

            type_element = row.find_element(By.XPATH, ".//td[4]").text.strip()
            kv_number = row.find_element(By.XPATH, ".//td[3]").text.strip()
            ser_number_element = row.find_element(By.XPATH, ".//td[8]").text.strip()
            active_element = row.find_element(By.XPATH, ".//td[10]").text.strip()
            start_poz_element = row.find_element(By.XPATH, ".//td[11]").text.strip()
            edin_element = row.find_element(By.XPATH, ".//td[12]").text.strip()
            karta_elem = row.find_element(By.XPATH, ".//td[13]").text.strip()
            is_pokazania = row.find_element(By.XPATH, ".//td[7]").text.strip()

            card_element = row.find_element(By.XPATH, ".//td[13]/input")

            # Получение значения атрибута onclick
            onclick_value = card_element.get_attribute("onclick")

            uid_match = re.search(r"uid:(\d+)", onclick_value)
            cid_match = re.search(r"cid:(\d+)", onclick_value)

            # Значения uid и cid
            uid = uid_match.group(1) if uid_match else None
            cid = cid_match.group(1) if cid_match else None

            if "ТОВ" not in name and "ПП" not in name and "-Інвест" not in name and active_element == "Открыто" and is_pokazania != "НЕТ":
                    # Выводим результаты
                    print("Имя:", name)
                    print("Type:", type_element)
                    print("Ser_number:", ser_number_element)
                    print("Active:", active_element)
                    print("Start_poz:", start_poz_element)
                    print("Edin:", edin_element)
                    print("Karta:", karta_elem)
                    print("uid", uid)
                    print("cid", cid)

                    print("=" * 50)

                    odata_url = f'{BD_HOST}Catalog_ПриборыУчета?$format=json&$filter=ЗаводскойНомер eq \'{ser_number_element}\''
                    print(odata_url)
                    response = session.get(odata_url , headers={'Content-Type': 'application/json; charset=utf-8'})
#                         print(response.status_code, response.json())
                    if response.status_code == 200:
                        response = response.json()
                        if len(response.get('value', [])) > 0:
                            code_pribor = response['value'][0]["Code"]


                            yslyga_code = None
                            if type_element == "Счетчик электрический":
                                yslyga_code = "000000016"
                            elif type_element == "Счетчик холодной воды":
                                yslyga_code = "000000048"
                            elif type_element == "Счетчик тепла отопления":
                                yslyga_code = "000000009"
                            elif type_element == "Счетчик горячей воды":
                                yslyga_code = "000000044"

                            izmerenie_code = None
                            if edin_element == "МВт" or edin_element == "ГДж" or edin_element == "Гкал":
                                izmerenie_code = "Гкал"
                            elif edin_element == "КВт/час":
                                izmerenie_code = "кВт·год"
                            elif edin_element == "куб.м.":
                                izmerenie_code = "м3"
                            elif edin_element == "КВт(Тепло)":
                                izmerenie_code = "кВт"


                            if is_pokazania != "НЕТ":
                                pokazania_list = []
                                try:

                                    pokazania_url = f"https://admin.asn.od.ua/frontend/frontend.php?myname=cvl&uid={uid}&cid={cid}&op=form&do_form=1&parent_win_id=winp_17&win_id=winp_18"


                                    # Открытие новой вкладки
                                    driver.execute_script("window.open('https://www.example.com', '_blank');")

                                    # Получение списка идентификаторов вкладок
                                    handles = driver.window_handles

                                    # Переключение на новую вкладку
                                    driver.switch_to.window(handles[1])

                                    # Работа с новой вкладкой (например, выполнение каких-то действий)

                                    driver.get(pokazania_url)

                                    pokaz_rows = driver.find_elements(By.XPATH, "//tr")

                                    # Перебираем каждый элемент <tr>
                                    for pokaz_row in pokaz_rows[1:]:
                                        pokaz_data = pokaz_row.find_element(By.XPATH, ".//td[1]").text.strip()
                                        pokaz_prev = pokaz_row.find_element(By.XPATH, ".//td[2]").text.strip()
                                        pokaz_new = pokaz_row.find_element(By.XPATH, ".//td[3]").text.strip()

                                        print(pokaz_data, pokaz_prev, pokaz_new)

                                        совпадение = re.search(r'\d{2}.\d{2}.\d{4} \d{2}:\d{2}', pokaz_data)
                                        строкаДатаВремя = совпадение.group(0)

                                        # Преобразуем строку даты и времени в формате строки
                                        толькоДата = datetime.strptime(строкаДатаВремя, '%d.%m.%Y %H:%M').strftime('%d.%m.%Y')



                                        pokazania_list.append({"ДатаУстановки": perform_data(толькоДата), "ПрошлоеПоказание": pokaz_prev, "НачальноеПоказание": pokaz_new})
                                    print("-" * 50)


                                    # Закрытие новой вкладки


                                    driver.close()

                                    # Переключение обратно на первую вкладку (если необходимо)
                                    driver.switch_to.window(handles[0])
                                except Exception as e:
                                    breakpoint()
                                    print(e)

                                odata_url = f'{BD_HOST}Catalog_ЛицевыеСчета?$format=json&$expand=ОбъектЛицевогоСчета&$filter=ОбъектЛицевогоСчета/Description eq \'{process_string_kv(kv_number)}\''
                                print(odata_url)
                                response = session.get(odata_url , headers={'Content-Type': 'application/json; charset=utf-8'})
                                lic_chet = ""
                                if response.status_code == 200:
                                    response = response.json()
                                    if len(response.get('value', [])) > 0:
                                        print(f"Exists {len(response.get('value', []))}")
                                        lic_chet = response['value'][0]["Description"]


                                for i in pokazania_list:


                                    data = {"КодУслуги": yslyga_code,"КодЗдания": "000000001",  "ОрганизацияКод": "00-000001", "ОбъектУстановки": lic_chet,  "ОбъектУстановки2": process_string_kv(kv_number), "СтрокаДата": i["ДатаУстановки"], "КодПриборУчета": code_pribor, "ПоказаниеПредыдущее": i["ПрошлоеПоказание"], "Показание": i["НачальноеПоказание"]}
                                    breakpoint()
                                    response = session.post('http://osbb.tais-dtb.com:8280/OSBB/hs/API/Ввод' , headers={'Content-Type': 'application/json; charset=utf-8'}, json=data)
                                    if response.status_code != 200:
                                        print(response.status_code, response.text)
                                        breakpoint()
                                    else:
                                        print(f"Прибор учета {ser_number_element} успешно добавлен для лицевого счета {lic_chet}")
                                        print("Exist")

                                print("-----------------------")

                            else:
                                print('No pokazania')









        except Exception as e:
            print(e)
            breakpoint()
            Error_list.append({"name": name, "response": response})


def parse_nachislenia(driver, session):
        url_sait = "https://admin.asn.od.ua/frontend/frontend.php?storevars=1&form_id=srkf_form&uriid=0&do_system=1&mod=nl&but_name=&page=&pagesize=&pagesmax=&do_dom=1&dom_default=523&dom=523&ugroup=1097&ugroup_option=0&lsstr=%D0%9E%D1%81%D0%B0%D0%B4%D1%87%D0%B0&do_lsid=1&lsid=12007&type_id_default=203&type_id=204&type_id_t=0&avars%5B%5D=do_kv_num&avars%5B%5D=kv_num_type&avars%5B%5D=kv_num_t&avars%5B%5D=kv_num&kv_num=5-%D0%90&kv_num_t=1&do_date_do=1&date_do=202402&date1=2024-02-01&date2=2023-12-01&abon=kp&subrah=ct.1&do_serv=1&serv=abon&variant=ppl&sbtn0=%D0%9F%D0%BE%D0%B8%D1%81%D0%BA&myname=nll&do_select=1&do_form=1&do_create=1"

        skip = False
        tip = "204"
        try:
            driver.get(url_sait)
            time.sleep(1)
            # Находим все элементы <tr> с помощью XPath
            rows = driver.find_elements(By.XPATH, "//tr[contains(@id, 'row_')]")
        except Exception as e:
            skip = True
            print("Error", e, " skip")

        data = []
        if not skip:
        # Перебираем каждый элемент <tr>
            not_sorted_data = []
            iiter = 1
            try:
                for row in rows[1:]:
                    # Извлекаем имя из элемента <b> внутри текущего <tr>

                        name = row.find_element(By.XPATH, ".//td[3]").text.strip()
                        parse_obj = row.find_element(By.XPATH, ".//td[4]").text.strip()
                        tip_obj = row.find_element(By.XPATH, ".//td[7]").text.strip()
                        parse_coment = row.find_element(By.XPATH, ".//td[9]").text.strip()
                        parse_data = row.find_element(By.XPATH, ".//td[10]").text.strip()
                        parse_znach = row.find_element(By.XPATH, ".//td[11]").text.strip()
                        parse_summa = row.find_element(By.XPATH, ".//td[13]").text.strip()





                        if "ТОВ" not in name and "ПП" not in name and "-Інвест" not in name and "Аккаунт для тестів" not in name:
                                # Выводим результаты
                                print("Имя:", name)
                                print("Parse_obj:", parse_obj)
                                print("Tip_obj:", tip_obj)
                                print("Parse_coment:", parse_coment)
                                print("Parse_data:", parse_data)
                                print("Parse_znach:", parse_znach)
                                print("Parse_summa:", parse_summa)

                                print("=" * 50)

                                not_sorted_data.append({"name": name, "parse_obj": parse_obj, "tip_obj": tip_obj, "parse_coment": parse_coment, "parse_data": parse_data, "parse_znach": parse_znach, "parse_summa": parse_summa})



                sorted_data = []
                sorted_data = sorted(not_sorted_data, key=itemgetter("parse_obj", "parse_data"))

                # Группируем данные по значениям Parse_obj и Parse_data
                result = []
                for _, group in itertools.groupby(sorted_data, key=itemgetter("parse_obj", "parse_data")):
                    result.append(list(group))
            except Exception as e:
                print(e)


            try:

                for current_spisok in result:

                        is_lic_name = process_string_type(current_spisok[0]["parse_obj"], tip)
                        print(is_lic_name)
                        odata_url = f'{BD_HOST}Catalog_ЛицевыеСчета?$format=json&$expand=ОбъектЛицевогоСчета&$filter=ОбъектЛицевогоСчета/Description eq \'{is_lic_name}\''
                        print(odata_url)
                        response = session.get(odata_url , headers={'Content-Type': 'application/json; charset=utf-8'})

#                         print(response.status_code, response.json())
                        if response.status_code == 200:
                            response = response.json()
                            if len(response.get('value', [])) > 0:
                                print(f"Exists {len(response.get('value', []))}")
                                lic_chet_code = response['value'][0]["Description"]
                                lic_chet_code_main = response['value'][0]["Code"]


                                current_data = current_spisok[0]['parse_data']
                                совпадение = re.search(r'\d{2}:\d{2} \d{2}.\d{2}.\d{4}', current_data)
                                строкаДатаВремя = совпадение.group(0)

                                # Преобразуем строку даты и времени в формате строки
                                толькоДата = datetime.strptime(строкаДатаВремя, '%H:%M %d.%m.%Y').strftime('%d.%m.%Y')
                                current_data = perform_data(толькоДата)

                                source_time = datetime.strptime(current_data, '%Y%m%d')

                                # Форматирование объекта datetime в нужный формат
                                result_time_str = source_time.strftime('%Y-%m-%dT00:00:00')


                                comments = ""
                                pribors_list = []
                                summa_doc = 0
                                for this_spisok in current_spisok:
                                    comments += this_spisok['parse_coment'] + " / "

                                    yslyga_code = None
                                    if "Електроенергія" in this_spisok["tip_obj"]:
                                        yslyga_code = "000000016"

                                    elif "Холодна вода" in this_spisok["tip_obj"]:
                                        yslyga_code = "000000048"

                                    elif "Гаряча вода" in this_spisok["tip_obj"]:
                                        yslyga_code = "000000044"

                                    elif "Опалення" in this_spisok["tip_obj"]:
                                        yslyga_code = "000000009"

                                    elif "УБПТ" in this_spisok["tip_obj"]:
                                        yslyga_code = "000000002"

                                    elif "Парковка" in this_spisok["tip_obj"]:
                                        yslyga_code = "000000039"

                                    elif "Парковка" in this_spisok["tip_obj"]:
                                        yslyga_code = "Р00000110"

                                    elif "Кладові" in this_spisok["tip_obj"]:
                                        yslyga_code = "Р00000110"

                                    elif "Вивіз сміття" in this_spisok["tip_obj"]:
                                        yslyga_code = "000000038"

                                    elif "Утримання котельні" in this_spisok["tip_obj"]:
                                        yslyga_code = "000000007"

                                    elif "Охрана" in this_spisok["tip_obj"]:
                                        yslyga_code = "000000028"

                                    try:
                                       single_summa = float(this_spisok["parse_summa"].replace(" ", "").replace(",","."))
                                    except Exception as e:
                                        print("!!!!!!! Problem with", this_spisok["parse_summa"])
                                        print(e)
                                        single_summa = 0


                                    pribors_list.append({"КодУслуги": yslyga_code,
                                        "ЛицевойСчетИмя": lic_chet_code_main,
                                        "СуммаНачислено": single_summa,
                                        "Количество": this_spisok["parse_znach"]
                                    })




                                    summa_doc += single_summa






                                odata_url = f'{BD_HOST}Document_НачислениеПоЛС?$format=json&$filter=СуммаДокумента eq {summa_doc} and Услуги/ЛицевойСчет/Description eq \'{lic_chet_code}\' and Date eq datetime\'{result_time_str}\''
                                print(odata_url)
                                response = session.get(odata_url , headers={'Content-Type': 'application/json; charset=utf-8'})
        #                         print(response.status_code, response.json())
                                if response.status_code == 200:
                                    response = response.json()

                                    if len(response.get('value', [])) > 0:

                                        data = {"Коментарий": comments,   "КодЗдания": "000000001",  "ОрганизацияКод": "00-000001", "СтрокаДата": current_data, "ПриборыУчета": pribors_list}

                                        response = session.post('http://osbb.tais-dtb.com:8280/OSBB/hs/API/Начисления' , headers={'Content-Type': 'application/json; charset=utf-8'}, json=data)
                                        if response.status_code != 200:
                                            print(response.status_code, response.text)

                                            Error_list.append({"name": lic_chet_code, "response": response.text})

                                        else:
                                            print(f"Начисление успешно добавлено для лицевого счета")
                                    else:

                                        data = {"Коментарий": comments, "КодЗдания": "000000001",
                                                "ОрганизацияКод": "00-000001", "СтрокаДата": current_data,
                                                "ПриборыУчета": pribors_list}

                                        response = session.post('http://osbb.tais-dtb.com:8280/OSBB/hs/API/Начисления',
                                                                headers={
                                                                    'Content-Type': 'application/json; charset=utf-8'},
                                                                json=data)
                                        if response.status_code != 200:
                                            print(response.status_code, response.text)

                                            Error_list.append({"name": lic_chet_code, "response": response.text})

                                        else:
                                            print(f"Начисление успешно добавлено для лицевого счета")

                                else:
                                    print(response)
                                    breakpoint()





                            else:
                                print("Нет такого лицевого счета")
                        else:
                            print("Ошибка такого лицевого счета")



            except Exception as e:
                print(e)
                breakpoint()
                Error_list.append({"name": name, "response": response})


        print(Error_list)

def extract_data(input_string):
    # Регулярное выражение для извлечения номера квартиры
    regex_pattern = re.compile(r'кв\.\s*(\d+)')

    # Поиск совпадений
    match = regex_pattern.search(input_string)

    # Если найдено совпадение
    if match:
        # Вывод информации о квартире
        apartment_number = match.group(1)
        print(f"Найдены данные о квартире: {apartment_number}")
        return apartment_number

    else:
        return None

def extract_date(input_string):
    # Регулярное выражение для извлечения даты "07.2023"
    regex_pattern = re.compile(r'(\d{2}\.\d{4})')

    # Поиск совпадений
    match = regex_pattern.search(input_string)

    # Если найдено совпадение
    if match:
        # Извлечение даты
        date_string = match.group(1)
        return date_string
    else:
        print("Дата не найдена")
        return None


def extract_storage_number(input_string):
    # Регулярное выражение для извлечения числа после "к"
    regex_pattern = re.compile(r'к(\d+)-\S+')

    # Поиск совпадений
    match = regex_pattern.search(input_string)

    # Если найдено совпадение
    if match:
        # Извлечение числа
        storage_number = match.group(1)
        print(f"Найден номер кладовой: {storage_number}")
        return storage_number
    else:
        print("Номер кладовой не найден")
        return None


from calendar import monthrange

def add_last_day_of_month(date_string):
    # Разделение строки на месяц и год
    month, year = map(int, date_string.split('.'))

    # Определение последнего дня месяца
    last_day = monthrange(year, month)[1]

    # Формирование строки с добавлением последнего дня месяца
    result_string = f"01.{date_string}"

    return result_string
def  parse_oplata(driver, session):
    list_obj = [ '12001', '12002', '12003', '12004', '12005', '12006', '12563', '12008', '12009', '12010', '12012', '12013', '12014', '12015', '12016', '12017', '12018', '12019', '12020', '12021', '12022', '12023', '12024', '12025', '12026', '12027', '12028', '12029', '12030', '12031', '12032', '12033', '12034', '12035', '12036', '12037', '12039', '12040', '12041', '12042', '12043', '12044', '12045', '12046', '12047', '12048', '12049', '12050', '12051', '12052', '12053', '12054', '12055', '12056', '12057', '12058', '12059', '12060', '12061', '12062', '12063', '12064', '12065', '12066', '12067', '12068', '12069', '12070', '12071', '12072', '12073', '12074', '12075', '12076', '12077', '12078', '12079', '12080', '12081', '12553', '12082', '12083', '12084', '12085', '12086', '12087', '12088', '12089', '12090', '12091', '12092', '12093', '12094', '12095', '12096', '12097', '12098', '12099', '12100', '12101', '12102', '12103', '12104', '12105', '12106', '12107', '12108', '12110', '12111', '12112', '12113', '12114', '12115', '12116', '12117', '12118', '12119', '12120', '12121', '12570', '12123', '12124', '12125', '12126', '12127', '12128', '12129', '12130', '12131', '12132', '12133', '12134', '12135', '12136', '12137', '12138', '12139', '12140', '12567', '12142', '12143', '12144', '12145', '12146', '12147', '12148', '12149', '12150', '12151', '12152', '12153', '12154', '12155', '12156', '12157', '12158', '12159', '12160', '12210', '12162', '12550', '12551', '12552', '12163', '12164', '12165', '12166', '12167', '12568', '12168', '12169', '12170', '12171', '12172', '12173', '12174', '12175', '12176', '12177', '12178', '12179', '12180','12181', '12182', '12183', '12184', '12185', '12186', '12187', '12188', '12189', '12190', '12191', '12192', '12193', '12194', '12195', '12196', '12197', '12198', '12199', '12200', '12201', '12202', '12203', '12204', '12109', '12205', '12206', '12207', '12208', '12209', '12141', '12122', '12564', '12161']

    for obj_num in list_obj:


        url_sait = f"https://admin.asn.od.ua/print/rah_prn3.php?user_id={obj_num}"
        skip = False
        tip = "203"
        try:
            driver.get(url_sait)
            time.sleep(1)
            # Находим все элементы <tr> с помощью XPath
            rows = driver.find_elements(By.XPATH, "//table[@id='table_rah']")
        except Exception as e:
            skip = True
            print("Error", e, " skip")

        data = []
        if not skip:
            # Перебираем каждый элемент <tr>
            not_sorted_data = []
            iter = 1
            try:
                parsed_name = None
                parsed_data = None
                for row in rows:
                    # Извлекаем имя из элемента <b> внутри текущего <tr>

                    if iter == 1:
                        name = row.find_element(By.XPATH, ".//span[@style=' font-family: Arial; font-size: 9pt;  font-weight: bold;']").text.strip()
                        parsed_name = extract_data(name)

                        iter += 1





                    if parsed_name and "ТОВ" not in parsed_name and "ПП" not in parsed_name and "-Інвест" not in parsed_name and "Аккаунт для тестів" not in parsed_name:
                        print(f"Find {parsed_name}")
                        tip_obj = row.find_elements(By.XPATH, ".//table[@class='table1']//td[2]")
                        oplata_sum = row.find_elements(By.XPATH, ".//table[@class='table1']//td[8]")

                        data_list = row.find_element(By.XPATH, ".//span[@style='font-family:Arial;font-size:10pt;font-weight: bold;']").text.strip()
                        parsed_data_def = extract_date(data_list)

                        parsed_data = add_last_day_of_month(parsed_data_def)
                        толькоДата = datetime.strptime(parsed_data, '%d.%m.%Y').strftime('%d.%m.%Y')
                        current_data = perform_data(толькоДата)

                        is_lic_name = process_string_type(parsed_name, "203")
                        print(is_lic_name)
                        odata_url = f'{BD_HOST}Catalog_ЛицевыеСчета?$format=json&$expand=ОбъектЛицевогоСчета&$filter=ОбъектЛицевогоСчета/Description eq \'{is_lic_name}\''
                        print(odata_url)
                        response = session.get(odata_url, headers={'Content-Type': 'application/json; charset=utf-8'})

                        #                         print(response.status_code, response.json())
                        if response.status_code == 200:
                            response = response.json()
                            if len(response.get('value', [])) > 0:
                                print(f"Exists {len(response.get('value', []))}")
                                lic_chet_code = response['value'][0]["Description"]
                                lic_chet_code_main = response['value'][0]["Code"]
                                pribors_list = []
                                comments = ""
                                summa_doc = 0
                                for i in range(len(tip_obj)):
                                        tip_str = tip_obj[i].text.strip()
                                        oplata_sum_str = oplata_sum[i].text.strip()
                                        comments += tip_str + " / "

                                        yslyga_code = None
                                        if "Електроенергія" in tip_str:
                                            yslyga_code = "000000016"

                                        elif "Холодна вода" in tip_str:
                                            yslyga_code = "000000048"

                                        elif "Гаряча вода" in tip_str:
                                            yslyga_code = "000000044"

                                        elif "Опалення" in tip_str:
                                            yslyga_code = "000000009"

                                        elif "УБПТ" in tip_str:
                                            yslyga_code = "000000002"

                                        elif "Вивіз сміття" in tip_str:
                                            yslyga_code = "000000038"

                                        elif "Утримання котельні" in tip_str:
                                            yslyga_code = "000000007"

                                        elif "Охорона" in tip_str:
                                            yslyga_code = "000000028"

                                        elif "Перенесення боргів" in tip_str:
                                            yslyga_code = "Р00000002"

                                        elif "Нерегулярні витрати" in tip_str or "Послугі з налаштування автоматичного доступу" in tip_str or "Внески до цільового фонду на придбання дизельгенератора" in tip_str or "Внески на дизельне пальне" in tip_str:
                                            yslyga_code = "000000025"

                                        elif "Кладові" in tip_str:

                                            if tip_str.count('(') >= 2:
                                                try:
                                                    yslyga_code = "pass"
                                                    is_lic_name_yslyga = process_string_type(tip_str, "209")
                                                    print(is_lic_name_yslyga)
                                                    odata_url = f'{BD_HOST}Catalog_ЛицевыеСчета?$format=json&$expand=ОбъектЛицевогоСчета&$filter=ОбъектЛицевогоСчета/Description eq \'{is_lic_name_yslyga}\''
                                                    print(odata_url)
                                                    response = session.get(odata_url, headers={
                                                        'Content-Type': 'application/json; charset=utf-8'})
                                                    if response.status_code == 200:
                                                        response = response.json()
                                                        if len(response.get('value', [])) > 0:
                                                            print(f"Exists {len(response.get('value', []))}")
                                                            lic_chet_code = response['value'][0]["Description"]
                                                            lic_chet_code_main_yslyga = response['value'][0]["Code"]

                                                            try:
                                                                single_summa = float(
                                                                    oplata_sum_str.replace(" ", "").replace(",", "."))
                                                            except Exception as e:
                                                                print("!!!!!!! Problem with", oplata_sum_str)
                                                                print(e)
                                                                single_summa = 0

                                                            data = {"Коментарий": tip_str, "ЛицевойСчетИмя": lic_chet_code_main_yslyga,
                                                                    "ОрганизацияКод": "00-000001", "ОбщСумма": single_summa, "Аванс": False,
                                                                    "СтрокаДата": current_data, "ПриборыУчета": [{"КодУслуги": "Р00000109",
                                                                                 "Сумма": single_summa
                                                                                 }]}

                                                            response = session.post(
                                                                'http://osbb.tais-dtb.com:8280/OSBB/hs/API/Оплата',
                                                                headers={'Content-Type': 'application/json; charset=utf-8'},
                                                                json=data)
                                                            if response.status_code != 200:
                                                                print(response.status_code, response.text)
                                                                print("Попытка с Авансом")
                                                                data = {"Коментарий": tip_str,
                                                                        "ЛицевойСчетИмя": lic_chet_code_main_yslyga,
                                                                        "ОрганизацияКод": "00-000001",
                                                                        "ОбщСумма": single_summa, "Аванс": True,
                                                                        "СтрокаДата": current_data,
                                                                        "ПриборыУчета": [{"КодУслуги": "Р00000109",
                                                                                          "Сумма": single_summa
                                                                                          }]}

                                                                response = session.post(
                                                                    'http://osbb.tais-dtb.com:8280/OSBB/hs/API/Оплата',
                                                                    headers={
                                                                        'Content-Type': 'application/json; charset=utf-8'},
                                                                    json=data)
                                                                if response.status_code != 200:
                                                                    print(response.status_code, response.text)
                                                                    breakpoint()

                                                                    Error_list.append({"name": lic_chet_code, "response": response.text})

                                                            else:
                                                                print(f"Начисление успешно добавлено для УСЛУГИ")
                                                except Exception as e:
                                                    breakpoint()
                                                    print(e)
                                            else:
                                                yslyga_code = "Р00000109"

                                        elif "Парковка" in tip_str:

                                            if tip_str.count('(') >= 2:
                                                try:
                                                    yslyga_code = "pass"
                                                    is_lic_name_yslyga = process_string_type(tip_str, "204")
                                                    print(is_lic_name_yslyga)
                                                    odata_url = f'{BD_HOST}Catalog_ЛицевыеСчета?$format=json&$expand=ОбъектЛицевогоСчета&$filter=ОбъектЛицевогоСчета/Description eq \'{is_lic_name_yslyga}\''
                                                    print(odata_url)
                                                    response = session.get(odata_url, headers={
                                                        'Content-Type': 'application/json; charset=utf-8'})
                                                    if response.status_code == 200:
                                                        response = response.json()
                                                        if len(response.get('value', [])) > 0:
                                                            print(f"Exists {len(response.get('value', []))}")
                                                            lic_chet_code = response['value'][0]["Description"]
                                                            lic_chet_code_main_yslyga = response['value'][0]["Code"]

                                                            try:
                                                                single_summa = float(
                                                                    oplata_sum_str.replace(" ", "").replace(",", "."))
                                                            except Exception as e:
                                                                print("!!!!!!! Problem with", oplata_sum_str)
                                                                print(e)
                                                                single_summa = 0

                                                            data = {"Коментарий": tip_str,
                                                                    "ЛицевойСчетИмя": lic_chet_code_main_yslyga,
                                                                    "ОрганизацияКод": "00-000001",
                                                                    "ОбщСумма": single_summa,
                                                                    "СтрокаДата": current_data,
                                                                    "Аванс": False,
                                                                    "ПриборыУчета": [{"КодУслуги": "000000039",
                                                                                      "Сумма": single_summa
                                                                                      }]}

                                                            response = session.post(
                                                                'http://osbb.tais-dtb.com:8280/OSBB/hs/API/Оплата',
                                                                headers={'Content-Type': 'application/json; charset=utf-8'},
                                                                json=data)
                                                            if response.status_code != 200:
                                                                print(response.status_code, response.text)
                                                                data = {"Коментарий": tip_str,
                                                                        "ЛицевойСчетИмя": lic_chet_code_main_yslyga,
                                                                        "ОрганизацияКод": "00-000001",
                                                                        "Аванс": True,
                                                                        "ОбщСумма": single_summa,
                                                                        "СтрокаДата": current_data,
                                                                        "ПриборыУчета": [{"КодУслуги": "000000039",
                                                                                          "Сумма": single_summa
                                                                                          }]}

                                                                response = session.post(
                                                                    'http://osbb.tais-dtb.com:8280/OSBB/hs/API/Оплата',
                                                                    headers={
                                                                        'Content-Type': 'application/json; charset=utf-8'},
                                                                    json=data)
                                                                if response.status_code != 200:
                                                                    print(response.status_code, response.text)
                                                                    breakpoint()

                                                                    Error_list.append(
                                                                        {"name": lic_chet_code, "response": response.text})

                                                            else:
                                                                print(f"Начисление успешно добавлено для ПАРКОВКИ")
                                                except Exception as e:
                                                    breakpoint()
                                                    print(e)
                                            else:
                                                yslyga_code = "000000039"






                                        if yslyga_code != "pass":
                                            try:
                                                single_summa = float(
                                                    oplata_sum_str.replace(" ", "").replace(",", "."))
                                            except Exception as e:
                                                print("!!!!!!! Problem with", oplata_sum_str)
                                                print(e)
                                                single_summa = 0

                                            summa_doc += single_summa

                                            pribors_list.append({"КодУслуги": yslyga_code,
                                                                 "Сумма": single_summa
                                                                 })

                                data = {"Коментарий": comments, "ОбщСумма": summa_doc, "ЛицевойСчетИмя": lic_chet_code_main, "ОрганизацияКод": "00-000001", "СтрокаДата": current_data, "ПриборыУчета": pribors_list,  "Аванс": False}

                                response = session.post('http://osbb.tais-dtb.com:8280/OSBB/hs/API/Оплата', headers={'Content-Type': 'application/json; charset=utf-8'}, json=data)
                                if response.status_code != 200:
                                    print(response.status_code, response.text)
                                    data = {"Коментарий": comments, "ОбщСумма": summa_doc,
                                            "ЛицевойСчетИмя": lic_chet_code_main, "ОрганизацияКод": "00-000001",
                                            "СтрокаДата": current_data, "ПриборыУчета": pribors_list, "Аванс": True}

                                    response = session.post('http://osbb.tais-dtb.com:8280/OSBB/hs/API/Оплата',
                                                            headers={'Content-Type': 'application/json; charset=utf-8'},
                                                            json=data)
                                    if response.status_code != 200:
                                        print(response.status_code, response.text)
                                        breakpoint()
                                        Error_list.append({"name": lic_chet_code, "response": response.text})

                                else:
                                    print(f"Начисление успешно добавлено для лицевого счета")
                            else:
                                print("Нет такого лицевого счета")
                        else:
                            print("Ошибка такого лицевого счета")



            except Exception as e:
                print(e)
                breakpoint()
                Error_list.append({"name": name, "response": response})

    print(Error_list)


def parse_doplate(driver, session):
    url_sait = "https://admin.asn.od.ua/frontend/frontend.php?storevars=1&form_id=srkf_form&uriid=0&do_system=1&mod=nl&but_name=&page=&pagesize=&pagesmax=&do_dom=1&dom_default=523&dom=523&ugroup=1097&ugroup_option=0&lsstr=%D0%9E%D1%81%D0%B0%D0%B4%D1%87%D0%B0&do_lsid=1&lsid=12195&type_id_default=203&type_id=204&type_id_t=0&avars%5B%5D=do_kv_num&avars%5B%5D=kv_num_type&avars%5B%5D=kv_num_t&avars%5B%5D=kv_num&kv_num=49&kv_num_t=1&date_do=202402&date1=2024-02-01&date2=2023-12-01&abon=kp&subrah=ct.1&serv=abon&variant=ppl&sbtn0=%D0%9F%D0%BE%D0%B8%D1%81%D0%BA&myname=nll&do_select=1&do_form=1&do_create=1"



    skip = False
    tip = "203"
    name_kv = "кв. № 168"
    try:
        driver.get(url_sait)
        time.sleep(1)
        # Находим все элементы <tr> с помощью XPath
        rows = driver.find_elements(By.XPATH, "//tr[contains(@id, 'row_')]")
    except Exception as e:
        skip = True
        print("Error", e, " skip")

    data = []
    if not skip:
        # Перебираем каждый элемент <tr>
        not_sorted_data = []
        not_sorted_data_oplata = []
        iiter = 1
        try:
            for row in rows[1:]:
                # Извлекаем имя из элемента <b> внутри текущего <tr>

                name = row.find_element(By.XPATH, ".//td[3]").text.strip()
                parse_obj = row.find_element(By.XPATH, ".//td[4]").text.strip()
                tip_obj = row.find_element(By.XPATH, ".//td[7]").text.strip()
                parse_coment = row.find_element(By.XPATH, ".//td[9]").text.strip()
                parse_data = row.find_element(By.XPATH, ".//td[10]").text.strip()
                parse_znach = row.find_element(By.XPATH, ".//td[11]").text.strip()
                parse_oplata = row.find_element(By.XPATH, ".//td[12]").text.strip()
                parse_summa = row.find_element(By.XPATH, ".//td[13]").text.strip()

                if "ТОВ" not in name and "ПП" not in name and "-Інвест" not in name and "Аккаунт для тестів" not in name:
                    # Выводим результаты
                    print("Имя:", name)
                    print("Parse_obj:", parse_obj)
                    print("Tip_obj:", tip_obj)
                    print("Parse_coment:", parse_coment)
                    print("Parse_data:", parse_data)
                    print("Parse_znach:", parse_znach)
                    print("Parse_summa:", parse_summa)

                    print("=" * 50)
                    if parse_summa != "":
                        not_sorted_data.append(
                            {"name": name, "parse_obj": parse_obj, "tip_obj": tip_obj, "parse_coment": parse_coment,
                             "parse_data": parse_data, "parse_znach": parse_znach, "parse_summa": parse_summa})
                    elif parse_oplata != "":
                        not_sorted_data_oplata.append(
                            {"name": name, "parse_obj": parse_obj, "tip_obj": tip_obj, "parse_coment": parse_coment,
                             "parse_data": parse_data, "parse_znach": parse_znach, "parse_oplata": parse_oplata})
                    else:
                        pass

            sorted_data = []
            sorted_data_oplata = []
            sorted_data = sorted(not_sorted_data, key=itemgetter("parse_obj", "parse_data"))
            sorted_data_oplata = sorted(not_sorted_data_oplata, key=itemgetter("parse_obj", "parse_data"))

            # Группируем данные по значениям Parse_obj и Parse_data
            result = []
            for _, group in itertools.groupby(sorted_data, key=itemgetter("parse_obj", "parse_data")):
                result.append(list(group))
            result_oplata = []
            for _, group in itertools.groupby(sorted_data_oplata, key=itemgetter("parse_obj", "parse_data")):
                result_oplata.append(list(group))


        except Exception as e:
            print(e)

        try:

            for current_spisok in result:

                is_lic_name = name_kv
                print(is_lic_name)
                odata_url = f'{BD_HOST}Catalog_ЛицевыеСчета?$format=json&$expand=ОбъектЛицевогоСчета&$filter=ОбъектЛицевогоСчета/Description eq \'{is_lic_name}\''
                print(odata_url)
                response = session.get(odata_url, headers={'Content-Type': 'application/json; charset=utf-8'})

                #                         print(response.status_code, response.json())
                if response.status_code == 200:
                    response = response.json()
                    if len(response.get('value', [])) > 0:
                        print(f"Exists {len(response.get('value', []))}")
                        lic_chet_code = response['value'][0]["Description"]
                        lic_chet_code_main = response['value'][0]["Code"]

                        current_data = current_spisok[0]['parse_data']
                        совпадение = re.search(r'\d{2}:\d{2} \d{2}.\d{2}.\d{4}', current_data)
                        строкаДатаВремя = совпадение.group(0)

                        # Преобразуем строку даты и времени в формате строки
                        толькоДата = datetime.strptime(строкаДатаВремя, '%H:%M %d.%m.%Y').strftime('%d.%m.%Y')
                        current_data = perform_data(толькоДата)

                        source_time = datetime.strptime(current_data, '%Y%m%d')

                        # Форматирование объекта datetime в нужный формат
                        result_time_str = source_time.strftime('%Y-%m-%dT00:00:00')

                        comments = ""
                        pribors_list = []
                        summa_doc = 0
                        for this_spisok in current_spisok:
                            comments += this_spisok['parse_coment'] + " / "

                            yslyga_code = None
                            if "Електроенергія" in this_spisok["tip_obj"]:
                                yslyga_code = "000000016"

                            elif "Холодна вода" in this_spisok["tip_obj"]:
                                yslyga_code = "000000048"

                            elif "Гаряча вода" in this_spisok["tip_obj"]:
                                yslyga_code = "000000044"

                            elif "Опалення" in this_spisok["tip_obj"]:
                                yslyga_code = "000000009"

                            elif "УБПТ" in this_spisok["tip_obj"]:
                                yslyga_code = "000000002"

                            elif "Парковка" in this_spisok["tip_obj"]:
                                if this_spisok['parse_coment'].count('(') >= 2:
                                    try:
                                        yslyga_code = "000000039"
                                        is_lic_name_yslyga = process_string_type(this_spisok['parse_coment'], "204")
                                        print(is_lic_name_yslyga)
                                        odata_url = f'{BD_HOST}Catalog_ЛицевыеСчета?$format=json&$expand=ОбъектЛицевогоСчета&$filter=ОбъектЛицевогоСчета/Description eq \'{is_lic_name_yslyga}\''
                                        print(odata_url)
                                        response = session.get(odata_url, headers={
                                            'Content-Type': 'application/json; charset=utf-8'})
                                        if response.status_code == 200:
                                            response = response.json()
                                            if len(response.get('value', [])) > 0:
                                                print(f"Exists {len(response.get('value', []))}")
                                                lic_chet_code = response['value'][0]["Description"]
                                                lic_chet_code_main_yslyga = response['value'][0]["Code"]

                                                try:
                                                    single_summa = float(
                                                        this_spisok["parse_summa"].replace(" ", "").replace(",", "."))
                                                except Exception as e:
                                                    print("!!!!!!! Problem with", this_spisok["parse_summa"])
                                                    print(e)
                                                    single_summa = 0

                                                data = {"Коментарий": this_spisok['parse_coment'],
                                                        "КодЗдания": "000000001",
                                                        "ОрганизацияКод": "00-000001",
                                                        "СтрокаДата": current_data,
                                                        "ПриборыУчета": [{"КодУслуги": "000000039",
                                                                          "ЛицевойСчетИмя": lic_chet_code_main_yslyga,
                                                                          "СуммаНачислено": single_summa,
                                                                          "Количество": this_spisok["parse_znach"]
                                                                          }]}

                                                response = session.post(
                                                    'http://osbb.tais-dtb.com:8280/OSBB/hs/API/Начисления',
                                                    headers={'Content-Type': 'application/json; charset=utf-8'},
                                                    json=data)
                                                if response.status_code != 200:
                                                    print(response.status_code, response.text)
                                                    Error_list.append(
                                                        {"name": lic_chet_code, "response": response.text})

                                                else:
                                                    print(f"Начисление успешно добавлено для Парковка")
                                    except Exception as e:
                                        breakpoint()
                                        print(e)
                                else:
                                    yslyga_code = "000000039"


                            elif "Кладові" in this_spisok["tip_obj"]:
                                if this_spisok['parse_coment'].count('(') >= 2:
                                    try:
                                        yslyga_code = "Р00000110"
                                        is_lic_name_yslyga = process_string_type(this_spisok['parse_coment'], "209")
                                        print(is_lic_name_yslyga)
                                        odata_url = f'{BD_HOST}Catalog_ЛицевыеСчета?$format=json&$expand=ОбъектЛицевогоСчета&$filter=ОбъектЛицевогоСчета/Description eq \'{is_lic_name_yslyga}\''
                                        print(odata_url)
                                        response = session.get(odata_url, headers={
                                            'Content-Type': 'application/json; charset=utf-8'})
                                        if response.status_code == 200:
                                            response = response.json()
                                            if len(response.get('value', [])) > 0:
                                                print(f"Exists {len(response.get('value', []))}")
                                                lic_chet_code = response['value'][0]["Description"]
                                                lic_chet_code_main_yslyga = response['value'][0]["Code"]

                                                try:
                                                    single_summa = float(
                                                        this_spisok["parse_summa"].replace(" ", "").replace(",", "."))
                                                except Exception as e:
                                                    print("!!!!!!! Problem with", this_spisok["parse_summa"])
                                                    print(e)
                                                    single_summa = 0


                                                data = {"Коментарий": this_spisok['parse_coment'],
                                                        "КодЗдания": "000000001",
                                                        "ОрганизацияКод": "00-000001",
                                                        "СтрокаДата": current_data,
                                                        "ПриборыУчета": [{"КодУслуги": "Р00000109",
                                                                          "ЛицевойСчетИмя": lic_chet_code_main_yslyga,
                                                                          "СуммаНачислено": single_summa,
                                                                          "Количество": this_spisok["parse_znach"]
                                                                          }]}

                                                response = session.post(
                                                    'http://osbb.tais-dtb.com:8280/OSBB/hs/API/Начисления',
                                                    headers={'Content-Type': 'application/json; charset=utf-8'},
                                                    json=data)
                                                if response.status_code != 200:
                                                    print(response.status_code, response.text)
                                                    Error_list.append(
                                                            {"name": lic_chet_code, "response": response.text})

                                                else:
                                                    print(f"Начисление успешно добавлено для УСЛУГИ")
                                    except Exception as e:
                                        breakpoint()
                                        print(e)
                                else:
                                    yslyga_code = "Р00000110"

                            elif "Вивіз сміття" in this_spisok["tip_obj"]:
                                yslyga_code = "000000038"

                            elif "Утримання котельні" in this_spisok["tip_obj"]:
                                yslyga_code = "000000007"

                            elif "Охрана" in this_spisok["tip_obj"]:
                                yslyga_code = "000000028"
                            elif "Перенесення" in this_spisok["tip_obj"]:
                                yslyga_code = "Р00000002"

                            elif "Нерегулярные" in this_spisok["tip_obj"]:
                                yslyga_code = "000000025"
                            else:
                                yslyga_code = "000000025"


                            try:
                                single_summa = float(this_spisok["parse_summa"].replace(" ", "").replace(",", "."))
                            except Exception as e:
                                print("!!!!!!! Problem with", this_spisok["parse_summa"])
                                print(e)
                                single_summa = 0

                            pribors_list.append({"КодУслуги": yslyga_code,
                                                 "ЛицевойСчетИмя": lic_chet_code_main,
                                                 "СуммаНачислено": single_summa,
                                                 "Количество": this_spisok["parse_znach"]
                                                 })

                            summa_doc += single_summa


                        #                         print(response.status_code, response.json())


                        data = {"Коментарий": comments, "КодЗдания": "000000001", "ОрганизацияКод": "00-000001",
                                "СтрокаДата": current_data, "ПриборыУчета": pribors_list}



                        response = session.post('http://osbb.tais-dtb.com:8280/OSBB/hs/API/Начисления',
                                                headers={'Content-Type': 'application/json; charset=utf-8'},
                                                json=data)
                        if response.status_code != 200:
                            print(response.status_code, response.text)

                            Error_list.append({"name": lic_chet_code, "response": response.text})

                        else:
                            print(f"Начисление успешно добавлено для лицевого счета")


                    else:
                        print("Нет такого лицевого счета")
                else:
                    print("Ошибка такого лицевого счета")


            for current_spisok in result_oplata:

                is_lic_name = name_kv
                print(is_lic_name)
                odata_url = f'{BD_HOST}Catalog_ЛицевыеСчета?$format=json&$expand=ОбъектЛицевогоСчета&$filter=ОбъектЛицевогоСчета/Description eq \'{is_lic_name}\''
                print(odata_url)
                response = session.get(odata_url, headers={'Content-Type': 'application/json; charset=utf-8'})

                #                         print(response.status_code, response.json())
                if response.status_code == 200:
                    response = response.json()
                    if len(response.get('value', [])) > 0:
                        print(f"Exists {len(response.get('value', []))}")
                        lic_chet_code = response['value'][0]["Description"]
                        lic_chet_code_main = response['value'][0]["Code"]

                        current_data = current_spisok[0]['parse_data']
                        совпадение = re.search(r'\d{2}:\d{2} \d{2}.\d{2}.\d{4}', current_data)
                        строкаДатаВремя = совпадение.group(0)

                        # Преобразуем строку даты и времени в формате строки
                        толькоДата = datetime.strptime(строкаДатаВремя, '%H:%M %d.%m.%Y').strftime('%d.%m.%Y')
                        current_data = perform_data(толькоДата)

                        source_time = datetime.strptime(current_data, '%Y%m%d')

                        # Форматирование объекта datetime в нужный формат
                        result_time_str = source_time.strftime('%Y-%m-%dT00:00:00')

                        comments = ""
                        pribors_list = []
                        summa_doc = 0
                        for this_spisok in current_spisok:
                            comments += this_spisok['parse_coment'] + " / "

                            yslyga_code = None
                            if "Електроенергія" in this_spisok["tip_obj"]:
                                yslyga_code = "000000016"

                            elif "Холодна вода" in this_spisok["tip_obj"]:
                                yslyga_code = "000000048"

                            elif "Гаряча вода" in this_spisok["tip_obj"]:
                                yslyga_code = "000000044"

                            elif "Опалення" in this_spisok["tip_obj"]:
                                yslyga_code = "000000009"

                            elif "УБПТ" in this_spisok["tip_obj"]:
                                yslyga_code = "000000002"

                            elif "Кладові" in this_spisok["tip_obj"]:

                                if this_spisok['parse_coment'].count('(') >= 2:
                                    try:
                                        yslyga_code = "Р00000109"
                                        is_lic_name_yslyga = process_string_type(this_spisok['parse_coment'], "209")
                                        print(is_lic_name_yslyga)
                                        odata_url = f'{BD_HOST}Catalog_ЛицевыеСчета?$format=json&$expand=ОбъектЛицевогоСчета&$filter=ОбъектЛицевогоСчета/Description eq \'{is_lic_name_yslyga}\''
                                        print(odata_url)
                                        response = session.get(odata_url, headers={
                                            'Content-Type': 'application/json; charset=utf-8'})
                                        if response.status_code == 200:
                                            response = response.json()
                                            if len(response.get('value', [])) > 0:
                                                print(f"Exists {len(response.get('value', []))}")
                                                lic_chet_code = response['value'][0]["Description"]
                                                lic_chet_code_main_yslyga = response['value'][0]["Code"]

                                                try:
                                                    single_summa = float(
                                                        this_spisok["parse_oplata"].replace(" ", "").replace(",", "."))
                                                except Exception as e:
                                                    print("!!!!!!! Problem with", this_spisok["parse_oplata"])
                                                    print(e)
                                                    single_summa = 0

                                                data = {"Коментарий": this_spisok['parse_coment'],
                                                        "ЛицевойСчетИмя": lic_chet_code_main_yslyga,
                                                        "ОрганизацияКод": "00-000001", "ОбщСумма": single_summa,
                                                        "Аванс": False,
                                                        "СтрокаДата": current_data,
                                                        "ПриборыУчета": [{"КодУслуги": "Р00000109",
                                                                          "Сумма": single_summa
                                                                          }]}

                                                response = session.post(
                                                    'http://osbb.tais-dtb.com:8280/OSBB/hs/API/Оплата',
                                                    headers={'Content-Type': 'application/json; charset=utf-8'},
                                                    json=data)
                                                if response.status_code != 200:
                                                    print(response.status_code, response.text)
                                                    print("Попытка с Авансом")
                                                    data = {"Коментарий": this_spisok['parse_coment'],
                                                            "ЛицевойСчетИмя": lic_chet_code_main_yslyga,
                                                            "ОрганизацияКод": "00-000001",
                                                            "ОбщСумма": single_summa, "Аванс": True,
                                                            "СтрокаДата": current_data,
                                                            "ПриборыУчета": [{"КодУслуги": "Р00000109",
                                                                              "Сумма": single_summa
                                                                              }]}

                                                    response = session.post(
                                                        'http://osbb.tais-dtb.com:8280/OSBB/hs/API/Оплата',
                                                        headers={
                                                            'Content-Type': 'application/json; charset=utf-8'},
                                                        json=data)
                                                    if response.status_code != 200:
                                                        print(response.status_code, response.text)
                                                        breakpoint()

                                                        Error_list.append(
                                                            {"name": lic_chet_code, "response": response.text})

                                                else:
                                                    print(f"Начисление успешно добавлено для УСЛУГИ")
                                    except Exception as e:
                                        breakpoint()
                                        print(e)
                                else:
                                    yslyga_code = "Р00000109"

                            elif "Парковка" in this_spisok["tip_obj"]:

                                if this_spisok['parse_coment'].count('(') >= 2:
                                    try:
                                        yslyga_code = "000000039"
                                        is_lic_name_yslyga = process_string_type(this_spisok['parse_coment'], "204")
                                        print(is_lic_name_yslyga)
                                        odata_url = f'{BD_HOST}Catalog_ЛицевыеСчета?$format=json&$expand=ОбъектЛицевогоСчета&$filter=ОбъектЛицевогоСчета/Description eq \'{is_lic_name_yslyga}\''
                                        print(odata_url)
                                        response = session.get(odata_url, headers={
                                            'Content-Type': 'application/json; charset=utf-8'})
                                        if response.status_code == 200:
                                            response = response.json()
                                            if len(response.get('value', [])) > 0:
                                                print(f"Exists {len(response.get('value', []))}")
                                                lic_chet_code = response['value'][0]["Description"]
                                                lic_chet_code_main_yslyga = response['value'][0]["Code"]

                                                try:
                                                    single_summa = float(
                                                        this_spisok["parse_oplata"].replace(" ", "").replace(",", "."))
                                                except Exception as e:
                                                    print("!!!!!!! Problem with", this_spisok["parse_oplata"])
                                                    print(e)
                                                    single_summa = 0

                                                data = {"Коментарий": this_spisok['parse_coment'],
                                                        "ЛицевойСчетИмя": lic_chet_code_main_yslyga,
                                                        "ОрганизацияКод": "00-000001",
                                                        "ОбщСумма": single_summa,
                                                        "СтрокаДата": current_data,
                                                        "Аванс": False,
                                                        "ПриборыУчета": [{"КодУслуги": "000000039",
                                                                          "Сумма": single_summa
                                                                          }]}

                                                response = session.post(
                                                    'http://osbb.tais-dtb.com:8280/OSBB/hs/API/Оплата',
                                                    headers={'Content-Type': 'application/json; charset=utf-8'},
                                                    json=data)
                                                if response.status_code != 200:
                                                    print(response.status_code, response.text)
                                                    data = {"Коментарий": this_spisok['parse_coment'],
                                                            "ЛицевойСчетИмя": lic_chet_code_main_yslyga,
                                                            "ОрганизацияКод": "00-000001",
                                                            "Аванс": True,
                                                            "ОбщСумма": single_summa,
                                                            "СтрокаДата": current_data,
                                                            "ПриборыУчета": [{"КодУслуги": "000000039",
                                                                              "Сумма": single_summa
                                                                              }]}

                                                    response = session.post(
                                                        'http://osbb.tais-dtb.com:8280/OSBB/hs/API/Оплата',
                                                        headers={
                                                            'Content-Type': 'application/json; charset=utf-8'},
                                                        json=data)
                                                    if response.status_code != 200:
                                                        print(response.status_code, response.text)
                                                        breakpoint()

                                                        Error_list.append(
                                                            {"name": lic_chet_code, "response": response.text})

                                                else:
                                                    print(f"Начисление успешно добавлено для ПАРКОВКИ")
                                    except Exception as e:
                                        breakpoint()
                                        print(e)

                                elif "Нерегулярные" in this_spisok["tip_obj"]:
                                    yslyga_code = "000000025"
                                else:
                                    yslyga_code = "000000039"


                            elif "Вивіз сміття" in this_spisok["tip_obj"]:
                                yslyga_code = "000000038"

                            elif "Утримання котельні" in this_spisok["tip_obj"]:
                                yslyga_code = "000000007"

                            elif "Охрана" in this_spisok["tip_obj"]:
                                yslyga_code = "000000028"
                            elif "Перенесення" in this_spisok["tip_obj"]:
                                yslyga_code = "Р00000002"



                            try:
                                single_summa = float(this_spisok["parse_oplata"].replace(" ", "").replace(",", "."))
                            except Exception as e:
                                print("!!!!!!! Problem with", this_spisok["parse_oplata"])
                                print(e)
                                single_summa = 0

                            pribors_list.append({"КодУслуги": yslyga_code,
                                                 "Сумма": single_summa
                                                 })


                            summa_doc += single_summa

                        data = {"Коментарий": comments, "ОбщСумма": summa_doc, "ЛицевойСчетИмя": lic_chet_code_main,
                                "ОрганизацияКод": "00-000001", "СтрокаДата": current_data, "ПриборыУчета": pribors_list,
                                "Аванс": False}

                        response = session.post('http://osbb.tais-dtb.com:8280/OSBB/hs/API/Оплата',
                                                headers={'Content-Type': 'application/json; charset=utf-8'}, json=data)
                        if response.status_code != 200:
                            print(response.status_code, response.text)
                            data = {"Коментарий": comments, "ОбщСумма": summa_doc,
                                    "ЛицевойСчетИмя": lic_chet_code_main, "ОрганизацияКод": "00-000001",
                                    "СтрокаДата": current_data, "ПриборыУчета": pribors_list, "Аванс": True}

                            response = session.post('http://osbb.tais-dtb.com:8280/OSBB/hs/API/Оплата',
                                                    headers={'Content-Type': 'application/json; charset=utf-8'},
                                                    json=data)
                            if response.status_code != 200:
                                print(response.status_code, response.text)
                                Error_list.append({"name": lic_chet_code, "response": response.text})
                            else:
                                print(f"Начисление успешно добавлено для лицевого счета")

                        else:
                            print(f"Начисление успешно добавлено для лицевого счета")

                    else:
                        print("Нет такого лицевого счета")
                else:
                    print("Ошибка такого лицевого счета")




        except Exception as e:
            print(e)
            breakpoint()
            Error_list.append({"name": name, "response": response})

    print(Error_list)


def login(driver, session):
    driver.get("https://o26.osbb.od.ua/?tab=login")
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    time.sleep(1)
    try:
        # Вводим логин
        login_input = driver.find_element(By.ID, 'login')
        login_input.send_keys('o26.chief')

        # Вводим пароль
        password_input = driver.find_element(By.ID, 'password')
        password_input.send_keys('9a42dc6')

        # Нажимаем кнопку "Увійти"
        submit_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        submit_button.click()
    finally:
        # Закрываем браузер после выполнения действий
        pass


def main(type):
    driver = webdriver.Chrome()
    driver.maximize_window()

    session = requests.Session()
    session.auth = HTTPBasicAuth("Федоров".encode(encoding='UTF-8',errors='strict'), BD_PASSWORD)



    if type == 'person':
        parse_personal_info(driver, session)


    elif type == 'scheta':
        parse_scheta(driver, session)

    elif type == 'schetchiki':
        login(driver, session)
        parse_schetchiki(driver, session)

    elif type == 'schetchiki_doc':
        login(driver, session)
        parse_schetchiki_doc(driver, session)

    elif type == 'nachislenia':
        login(driver, session)
        parse_nachislenia(driver, session)

    elif type == 'oplata':
        login(driver, session)
        parse_oplata(driver, session)
    elif type == 'doplata':
        login(driver, session)
        parse_doplate(driver, session)
















if __name__ == '__main__':
        main(type='schetchiki_doc')

