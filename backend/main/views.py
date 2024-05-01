from django.contrib import messages
import jinja2
import pdfkit
from django.contrib.auth import login, authenticate, REDIRECT_FIELD_NAME, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView as BaseLogoutView, FormView
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme as is_safe_url
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from .utils import country_codes
from datetime import datetime, timedelta
from django.http import JsonResponse
import pytz


from .forms import (
    SignInViaUsernameForm, ChangeProfileForm, ChangePasswordPhoneForm, ChangePasswordCodeForm, ChangePasswordConfirmForm
)
from .models import Poll, Choice, Vote, SupportTicket, BackgroundModel, DIA as DIA_model
from django.urls import reverse_lazy
from .onec import OSBB
from collections import defaultdict
import calendar
import re
import random
import locale
from notifications.signals import notify
from liqpay import LiqPay
from django.contrib.auth.forms import PasswordResetForm
from .sms_api import send_sms
from .api_dia import DIA



osbb = OSBB()
dia = DIA()
locale.setlocale(locale.LC_TIME, 'uk_UA.UTF-8')
liqpay = LiqPay("bqCbtIAPI2JXLhmzFzfIjnvzoMZsCx+yCElEKuPJ5qkSV9k0V3hR4mhc8jSYMZBNAU+VQILGbqFT33GwUrHMCQ==",
                "JGJRnXQqoqg+51jXxpKS4+37aJ0EeL756g8VNLPGAuHQipVi8u7TGr7Kbm28vgVIEciSYtUg0Y26hLkRH+4sID0EJDGQu48W1W3GxoE14TF3ZrTnO42II88M0KOk2CjU")

def parse_date(date_str):
    return datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")


def mark_notifications_as_read(request):
    if request.method == 'POST':
        # Помечаем все уведомления пользователя как прочитанные
        request.user.notifications.mark_all_as_read()
        return JsonResponse({'status': 'success', 'ok': True})
    return JsonResponse({'status': 'error'})

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        lich_response = osbb.get_lich_user(self.request.user.username)
        if lich_response:
            result_dict = {}
            for item in lich_response:
                number = item["number"]
                name = item["name"]
                code = item["code"]
                if number in result_dict:
                    # Если запись существует, добавляем текущее имя к существующему значению
                    result_dict[number]["codes"].append(code)
                    result_dict[number]["names"].append(name)
                else:
                    # Если записи нет, создаем новую запись в словаре
                    result_dict[number] = {"codes": [code], "names": [name]}

            result_list_kv = []

            for key, value in result_dict.items():
                kv_codes = [code for code in value['codes'] if 'кв.' in value['names'][value['codes'].index(code)]]
                result_list_kv.append(
                    {"number": key, "codes": ', '.join(kv_codes[:1]), "names": ', '.join(value['names'])})


            if not self.request.session.get('lich'):
                self.request.session['lich'] = result_list_kv[0]['codes']
                self.request.session['lich_name'] = result_list_kv[0]['names']

            context['lich_selected'] = self.request.session.get('lich', result_list_kv[0]['codes'])
            try:
                selected_kv_data = [i for i in lich_response if i['code'] == context['lich_selected']][0]
            except Exception as e:
                selected_kv_data = None

            context['selected_kv_data'] = selected_kv_data
            ostatok_response = osbb.get_ostatok_user(context['lich_selected'])
            if ostatok_response:
                ostatok_value = ostatok_response.get('ostatok', 0).encode('latin1').decode('unicode-escape')
                ostatok_value = ''.join(ostatok_value.split()).replace(',', '.')

                context['ostatok'] = f"-{ostatok_value}" if float(ostatok_value) > 0 else str(ostatok_value)
                ukraine_timezone = pytz.timezone('Europe/Kiev')
                current_datetime_utc = datetime.now(pytz.utc)

                # Преобразуем в часовой пояс Украины
                current_datetime_ukraine = current_datetime_utc.astimezone(ukraine_timezone)

                # Форматируем дату и время в нужный формат
                formatted_datetime = current_datetime_ukraine.strftime("%Y-%m-%d %H:%M")
                context['formatted_datetime'] = formatted_datetime


            raschet_response = osbb.get_raschet_user(context['lich_selected'])
            if raschet_response:
                dolg = raschet_response['Долг']
                raschet = raschet_response['Расчёт']


                result = defaultdict(lambda: {"month_oplata":month_oplata,"month_dolg": month_dolg, "month_nachislenie": month_nachislenie, "services": defaultdict(lambda: {"единица": "", "тариф":"", "оплата": 0, "нарах": 0, "quantity_narah": 0, "name": "", "долг": 0}), "month_name": "", "second_month_name": ""})

                for entry in raschet:
                    month_oplata = 0.0
                    month_dolg = 0.0
                    month_nachislenie = 0.0
                    date_str = entry["Период"].split()[0]
                    date = datetime.strptime(date_str, "%d.%m.%Y")
                    month_key = date.strftime("%Y-%m")
                    month_name = f"{date.year} {calendar.month_name[date.month].capitalize()}"
                    second_month_name = f"{calendar.month_name[date.month].capitalize()} {date.year}"

                    service_name = entry["Услуга"]
                    #TO-DO првоерить почему услуга пустая
                    if len(service_name) == 0:
                        service_name = "Додаткові"

                    if "УБПТ" in service_name:
                        ed_izm = "кв.м."
                        tarif = 8.35
                    elif "Кладові" in service_name:
                        ed_izm = "кв.м."
                        tarif = 5
                    elif "Паркінг" in service_name:
                        ed_izm = "шт."
                        tarif = 205
                    elif "Вивезення" in service_name:
                        ed_izm = "Чел."
                        tarif = 0.34
                    elif "Холодне" in service_name:
                        ed_izm = "куб.м."
                        tarif = 35.16
                    elif "Електроенергія" in service_name:
                        ed_izm = "КВт/год"
                        tarif = 2.64
                    elif "Утримання котельні" in service_name:
                        ed_izm = "кв.м."
                        tarif = 2.50
                    elif "Охорона" in service_name:
                        ed_izm = "Грн."
                        tarif = 1.90
                    elif "Додаткові" in service_name:
                        ed_izm = "Грн."
                        tarif = 0
                    elif "Нерегулярні" in service_name:
                        ed_izm = "Грн."
                        tarif = 0
                    elif "Опалення" in service_name:
                        ed_izm = "КВт/год"
                        tarif = 17.87
                    else:
                        ed_izm = "Грн."
                        tarif = 0




                    if "Надходження" in entry["Регистратор"]:
                        oplata = round(float(re.sub(r'[^\d.,]', '', entry["Сумма"]).replace(',', '.')), 2)

                        result[month_key]["services"][service_name]["оплата"] = round(float(result[month_key]["services"][service_name]["оплата"]) + float(oplata), 2)

                        result[month_key]["month_oplata"] += round(oplata, 2)
                        result[month_key]["month_oplata"] = round(result[month_key]["month_oplata"], 2)


                    elif "Нарахування" in entry["Регистратор"]:
                        oplata = round(float(re.sub(r'[^\d.,]', '', entry["Сумма"]).replace(',', '.')), 2)
                        result[month_key]["services"][service_name]["нарах"] += oplata
                        result[month_key]["month_nachislenie"] += round(oplata, 2)
                        result[month_key]["month_nachislenie"] = round(result[month_key]["month_nachislenie"], 2)
                        if int(re.sub(r'\D', '', entry["Количество"])) != 0:
                            colich =  float(re.sub(r'[^\d.,]', '',  entry["Количество"]).replace(',', '.'))
                            result[month_key]["services"][service_name]["quantity_narah"] = colich
                        else:
                            colich = 1

                    result[month_key]["services"][service_name]["единица"] = ed_izm
                    result[month_key]["services"][service_name]["тариф"] = tarif

                    result[month_key]["services"][service_name]["name"] = service_name
                    result[month_key]["month_name"] = month_name
                    result[month_key]["second_month_name"] = second_month_name



                for dolg_data in dolg:
                    date_str = dolg_data["МесяцНачисления"].split()[0]
                    date = datetime.strptime(date_str, "%d.%m.%Y")
                    month_key = date.strftime("%Y-%m")
                    month_name = f"{date.year} {calendar.month_name[date.month].capitalize()}"
                    service_name = dolg_data["Услуга"]
                    oplata = round(float(re.sub(r'[^\d.,]', '', dolg_data["СуммаОстаток"]).replace(',', '.')), 2)

                    # print(month_key)
                    # print(result[month_key]["services"][service_name]["долг"])
                    # print(float(result[month_key]["services"][service_name]["долг"]), oplata)
                    result[month_key]["services"][service_name]["долг"] = round(float(result[month_key]["services"][service_name]["долг"]) + float(oplata), 2)

                    result[month_key]["month_dolg"] += round(oplata, 2)
                    result[month_key]["month_dolg"] = round(result[month_key]["month_dolg"], 2)


                for month_data in result.values():
                    month_data["services"] = list(month_data["services"].values())

                result_list = [{"month": key, **values} for key, values in sorted(result.items(), reverse=True)]

                context['obw_summa'] = [{"month_oplata": i['month_oplata'],
                                         "month_nachislenie": i['month_nachislenie'],
                                         "second_month_name": i["second_month_name"]} for i in result_list]
                context['raschet'] = result_list


                # notify.send(self.request.user, recipient=self.request.user, verb=f'Перехід на головну сторінку {self.request.user.username}')

                sorted_data = {}
                dates = []

                formatted_data_2023 = [
                               {
                                  "label":"Електроенергія",
                                  "data":[],
                                  "borderWidth":1,
                                  "hoverOffset":4,

                                  "name":"Електроенергія",
                                  "year":2023,
                                  "backgroundColor":"rgba(255, 206, 86, 0.2)",
                                  "borderColor":"rgba(255, 206, 86, 1)"
                               },
                               {
                                  "label":"Холодна вода",
                                  "data":[],
                                  "borderWidth":1,
                                  "hoverOffset":4,
                                  "name":"Холодна вода",
                                  "year":2023,
                                  "backgroundColor":"rgba(153, 102, 255, 0.2)",
                                  "borderColor":"rgba(153, 102, 255, 1)"
                               },
                               {
                                  "label":"Опалення",
                                  "data":[],
                                  "borderWidth":1,
                                  "hoverOffset":4,
                                  "name":"Опалення",
                                  "year":2023,
                                  "backgroundColor":"rgba(255, 99, 132, 0.2)",
                                  "borderColor":"rgba(255, 99, 132, 1)"
                               },
                                {
                                    "label": "Інше",
                                    "data": [],
                                    "borderWidth": 1,
                                    "hoverOffset": 4,
                                    "name": "Інше",
                                    "year": 2023,
                                    "backgroundColor": 'rgba(75, 192, 192, 0.2)',
                                    "borderColor": 'rgba(75, 192, 192, 1)'
                                },
                            ]
                formatted_data_2024 = [
                               {
                                  "label":"Електроенергія",
                                  "data":[],
                                  "borderWidth":1,
                                  "hoverOffset":4,

                                  "name":"Електроенергія",
                                  "year":2024,
                                  "backgroundColor":"rgba(255, 206, 86, 0.2)",
                                  "borderColor":"rgba(255, 206, 86, 1)"
                               },
                               {
                                  "label":"Холодна вода",
                                  "data":[],
                                  "borderWidth":1,
                                  "hoverOffset":4,
                                  "name":"Холодна вода",
                                  "year":2024,
                                  "backgroundColor":"rgba(153, 102, 255, 0.2)",
                                  "borderColor":"rgba(153, 102, 255, 1)"
                               },
                               {
                                  "label":"Опалення",
                                  "data":[],
                                  "borderWidth":1,
                                  "hoverOffset":4,
                                  "name":"Опалення",
                                  "year":2024,
                                  "backgroundColor":"rgba(255, 99, 132, 0.2)",
                                  "borderColor":"rgba(255, 99, 132, 1)"
                               },
                                {
                                    "label": "Інше",
                                    "data": [],
                                    "borderWidth": 1,
                                    "hoverOffset": 4,
                                    "name": "Інше",
                                    "year": 2024,
                                    "backgroundColor": 'rgba(75, 192, 192, 0.2)',
                                    "borderColor": 'rgba(75, 192, 192, 1)'
                                },
                            ]
                colors = [
                    {'backgroundColor': 'rgba(255, 99, 132, 0.2)', 'borderColor': 'rgba(255, 99, 132, 1)'},
                    {'backgroundColor': 'rgba(54, 162, 235, 0.2)', 'borderColor': 'rgba(54, 162, 235, 1)'},
                    {'backgroundColor': 'rgba(255, 206, 86, 0.2)', 'borderColor': 'rgba(255, 206, 86, 1)'},
                    {'backgroundColor': 'rgba(75, 192, 192, 0.2)', 'borderColor': 'rgba(75, 192, 192, 1)'},
                    {'backgroundColor': 'rgba(153, 102, 255, 0.2)', 'borderColor': 'rgba(153, 102, 255, 1)'},
                    {'backgroundColor': 'rgba(255, 159, 64, 0.2)', 'borderColor': 'rgba(255, 159, 64, 1)'},
                    {'backgroundColor': 'rgba(255, 0, 0, 0.2)', 'borderColor': 'rgba(255, 0, 0, 1)'},
                    {'backgroundColor': 'rgba(0, 255, 0, 0.2)', 'borderColor': 'rgba(0, 255, 0, 1)'},
                    {'backgroundColor': 'rgba(0, 0, 255, 0.2)', 'borderColor': 'rgba(0, 0, 255, 1)'},
                    {'backgroundColor': 'rgba(255, 255, 0, 0.2)', 'borderColor': 'rgba(255, 255, 0, 1)'},
                    {'backgroundColor': 'rgba(255, 0, 255, 0.2)', 'borderColor': 'rgba(255, 0, 255, 1)'},
                    {'backgroundColor': 'rgba(0, 255, 255, 0.2)', 'borderColor': 'rgba(0, 255, 255, 1)'},
                    {'backgroundColor': 'rgba(128, 128, 128, 0.2)', 'borderColor': 'rgba(128, 128, 128, 1)'},
                    {'backgroundColor': 'rgba(0, 0, 0, 0.2)', 'borderColor': 'rgba(0, 0, 0, 1)'}
                ]
                # Получение месяцев для 2023 года
                result_months_2023 = []

                # Получение месяцев для 2024 года
                result_months_2024 = []

                for entry in result_list:
                    try:

                        month=entry['month']
                        if month != '2023-06' and month != '1-01':
                            total_for_month = entry['month_nachislenie']
                            is_water, is_otop, is_svet = False, False, False

                            total_exist_for_month = 0
                            for service in entry['services']:
                                service_name = service['name']
                                service_money = service['нарах']

                                if "Холодне" in service_name:
                                    is_water = True
                                    label_name = "Холодна вода"
                                    pos = 1
                                elif "Електроенергія" in service_name:
                                    is_svet = True
                                    label_name = "Електроенергія"
                                    pos = 0
                                elif "Опалення" in service_name:
                                    is_otop = True
                                    label_name = "Опалення"
                                    pos = 2
                                else:
                                    label_name = "Інше"
                                    pos = 3

                                if pos < 3:
                                    total_exist_for_month += service_money
                                    if '2024' in month:
                                        formatted_data_2024[pos]['data'].append(service_money)
                                    elif '2023' in month:
                                        formatted_data_2023[pos]['data'].append(service_money)



                            money_give = total_for_month - total_exist_for_month
                            date_obj = datetime.strptime(month, "%Y-%m")
                            month_name = date_obj.strftime("%B")
                            month_ukr_name = month_name[:3]
                            if '2024' in month:
                                if not is_water:
                                    formatted_data_2024[1]['data'].append(0)
                                if not is_svet:
                                    formatted_data_2024[0]['data'].append(0)
                                if not is_otop:
                                    formatted_data_2024[2]['data'].append(0)
                                formatted_data_2024[3]['data'].append(money_give)
                                result_months_2024.append(month_ukr_name)
                            elif '2023' in month:
                                if not is_water:
                                    formatted_data_2023[1]['data'].append(0)
                                if not is_svet:
                                    formatted_data_2023[0]['data'].append(0)
                                if not is_otop:
                                    formatted_data_2023[2]['data'].append(0)
                                formatted_data_2023[3]['data'].append(money_give)
                                result_months_2023.append(month_ukr_name)
                    except Exception as e:
                        pass









                context['yslygi_2023_chart'] = formatted_data_2023
                context['yslygi_2024_chart'] = formatted_data_2024

                context['available_months_list_2023'] = result_months_2023
                context['available_months_list_2024'] = result_months_2024



        else:
            result_list_kv = []
            context['formatted_datetime'] = "Спробуйте пізніше"
            context['ostatok'] = "-0"
            result = {
                "services": {"оплата": 0, "нарах": 0, "quantity_narah": 0, "name": ""},
                "month_name": ""}
            context['raschet'] = [result]
        context['lich'] = result_list_kv
        return context

    def post(self, request, *args, **kwargs):

        data = request.POST.get('data')
        if data:

            def number_to_words_uk(n, cents=False):
                """
                Функция преобразует число в текст на украинском языке.
                """
                units = ['', 'один', 'два', 'три', 'чотири', "п'ять", 'шість', 'сім', 'вісім', 'дев`ять']
                units22 = ['', 'одна', 'дві', 'три', 'чотири', "п'ять", 'шість', 'сім', 'вісім', 'дев`ять']
                teens = ['', 'одинадцять', 'дванадцять', 'тринадцять', 'чотирнадцять', "п'ятнадцять", 'шістнадцять',
                         'сімнадцять',
                         'вісімнадцять', 'дев`ятнадцять']
                tens = ['', '', 'двадцять', 'тридцять', 'сорок', "п'ятдесят", 'шістдесят', 'сімдесят', 'вісімдесят',
                        'дев`яносто']
                hundreds = ['', 'сто', 'двісті', 'триста', 'чотириста', "п'ятьсот", 'шістьсот', 'сімсот', 'вісімсот',
                            'дев`ятьсот']
                thousands = ['', 'тисяча', 'тисячі', 'тисячі', 'тисячі', 'тисяч', 'тисяч', 'тисяч', 'тисяч', 'тисяч']
                grivnas = ['гривня', 'гривні', 'гривень']
                copick = ['коп.']

                words = []

                if n == 0:
                    words.append('нуль')
                else:
                    num_str = str(n)
                    num_len = len(num_str)
                    padding = 6 - num_len
                    num_str = '0' * padding + num_str  # Дополняем нулями до 6 символов

                    thousands_3 = int(num_str[0])  # Тысячи сотни
                    thousands_2 = int(num_str[1])  # Тысячи сотни
                    thousands_1 = int(num_str[2])  # Тысячи десятки
                    hundreds_1 = int(num_str[3])  # Сотни
                    tens_1 = int(num_str[4])  ## Десятки
                    units_1 = int(num_str[5])  # Единицы

                    if cents:
                        if n > 0:
                            cents_1 = int(num_str[3:6])
                            if tens_1 == 1:
                                words.append(teens[units_1])
                            else:

                                words.append(tens[tens_1])
                                words.append(units[units_1])
                            words.append(copick[0])


                    else:

                        if thousands_1 > 0 or thousands_2 > 0 or thousands_3 > 0 or tens_1 > 0 or units_1 > 0:
                            if thousands_2 > 0:
                                words.append(tens[thousands_2])
                                words.append(units22[thousands_1])
                                words.append(thousands[thousands_2])
                            elif thousands_1 > 0:
                                words.append(units22[thousands_1])
                                words.append(thousands[thousands_1])
                            else:
                                words.append(thousands[0])

                            words.append(hundreds[hundreds_1])

                            if tens_1 == 1:
                                words.append(teens[units_1])
                            else:
                                words.append(tens[tens_1])
                                words.append(units22[units_1])

                            if units_1 == 1:
                                words.append(grivnas[0])
                            elif units_1 == 2:
                                words.append(grivnas[1])
                            else:
                                words.append(grivnas[2])

                return ' '.join(words)

            # Load the template

            from jinja2 import Environment, PackageLoader, select_autoescape
            env = jinja2.Environment(loader=PackageLoader("main"))

            template = env.get_template('tableTemplate.html')
            # pass df, title, message to the template.
            pdf_raw_data = json.loads(data)

            lich = self.request.session.get('lich')
            lich_selected_name = self.request.session.get('lich_name')

            raschet = [pdf_raw_data]
            user_info = self.request.user
            kv_name = f"{user_info.last_name} {user_info.first_name} {user_info.middle_name}"

            kv_ulica = f"провулок Обсерваторний, будинок 2/6, {lich_selected_name}"
            kv_nomer = lich
            kv_data_m = pdf_raw_data['month']
            kv_summa = pdf_raw_data['month_nachislenie']
            amount =  pdf_raw_data['month_nachislenie']
            amount_list = str(amount).split('.')
            if len(amount_list) > 1:
                amount_int = int(amount_list[0])
                amount_cents = int(amount_list[1])
            else:
                amount_int = int(amount_list[0])
                amount_cents = 0

            amount_in_words = number_to_words_uk(amount_int)
            if amount_cents > 0:
                amount_in_words += ", " + number_to_words_uk(amount_cents, True)

            kv_summa_letters = amount_in_words

            kv_data = {"kv_name": kv_name, "kv_ulica": kv_ulica, "kv_nomer": kv_nomer, "kv_data": kv_data_m,
                       "kv_summa": kv_summa, "amount_in_words": amount_in_words}

            html_out = template.render(raschet=raschet,
                                       kv_data=kv_data)
            options = {
                "enable-local-file-access": None
            }

            # write the html to file
            with open(f"main/media/temp/Рахунок_{kv_nomer}_{kv_data_m}.html", 'wb') as file_:
                file_.write(html_out.encode("utf-8"))

            # write the pdf to file
            pdfkit.from_string(html_out, output_path=f"main/media/temp/Рахунок_{kv_nomer}_{kv_data_m}.pdf", css=["main/template.css"], options=options)

            document_path = f"media/temp/Рахунок_{kv_nomer}_{kv_data_m}.pdf"

            # Отправить HTTP-ответ с ссылкой на скачивание файла
            return JsonResponse({'file_url': document_path})


class CountersView(LoginRequiredMixin, TemplateView):
    template_name = 'counters.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user

        lich = self.request.session.get('lich')
        if not lich:
            lich_response = osbb.get_lich_user(self.request.user.username)
            if lich_response:
                result_dict = {}
                for item in lich_response:
                    number = item["number"]
                    name = item["name"]
                    code = item["code"]
                    if number in result_dict:
                        # Если запись существует, добавляем текущее имя к существующему значению
                        result_dict[number]["codes"].append(code)
                        result_dict[number]["names"].append(name)
                    else:
                        # Если записи нет, создаем новую запись в словаре
                        result_dict[number] = {"codes": [code], "names": [name]}

                result_list = []

                for key, value in result_dict.items():
                    kv_codes = [code for code in value['codes'] if 'кв.' in value['names'][value['codes'].index(code)]]
                    result_list.append(
                        {"number": key, "codes": ', '.join(kv_codes[:1]), "names": ', '.join(value['names'])})

                lich_response = result_list

                context['lich_selected'] = result_list[0]['codes']
                context['lich_selected_name'] = result_list[0]['names']
        else:
            context['lich_selected'] = lich
            context['lich_selected_name'] = self.request.session.get('lich_name')
        yslygi_response = osbb.get_priboru_user(context['lich_selected'])
        pribory_response_list = osbb.get_unique_priboru_user(context['lich_selected'])
        if yslygi_response:
            sorted_data = {}

            dates = []
            for entry in yslygi_response:
                temp_entry_list = entry["ПриборУчета"].split('/')
                if len(temp_entry_list) > 2:
                    number = temp_entry_list[0] + '/' + temp_entry_list[1]
                    name = temp_entry_list[2]
                else:
                    number, name = temp_entry_list
                key = f"{number}/{name}"
                #year = datetime.strptime(entry["Период"], "%d.%m.%Y %H:%M:%S").year
                if key not in sorted_data:
                    sorted_data[key] = []
                sorted_data[key].append(entry)
                dates.append(datetime.strptime(entry["Период"], "%d.%m.%Y %H:%M:%S"))



            # Нахождение самой маленькой даты
            min_date = min(dates)

            date_range = []
            current_date = min_date
            while current_date <= datetime.now():
                date_range.append(current_date.replace(day=1))
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)

            formatted_data = {}
            for priboru_key in pribory_response_list:
                for data_motn in date_range:
                    name_key = priboru_key['ПриборУчета']
                    month_key = f"{data_motn.year} {calendar.month_name[data_motn.month].capitalize()}"
                    added_data = None
                    current_pribor_data = sorted_data.get(name_key)
                    if current_pribor_data:

                        max_date = ""

                        for entry in current_pribor_data:
                            period = parse_date(entry["Период"])
                            period_str = f"{period.year} {calendar.month_name[period.month].capitalize()}"

                            if period_str == month_key:
                                if max_date <= period_str:
                                    max_date = period_str
                                temp_entry_list = entry["ПриборУчета"].split('/')
                                if len(temp_entry_list) > 2:
                                    number = temp_entry_list[0] + '/' + temp_entry_list[1]
                                    name = temp_entry_list[2]
                                else:
                                    number, name = temp_entry_list
                                data_key_temp = data_motn - timedelta(days=data_motn.day)
                                month_key_temp = f"{data_key_temp.year} {calendar.month_name[data_key_temp.month].capitalize()}"

                                prev_month_data = formatted_data.get(month_key_temp, [])
                                pokaz_prev = 0
                                for i in prev_month_data:
                                    if i["ПриборУчета"] == entry["ПриборУчета"]:
                                        pokaz_prev = i["Pokaz"]

                                month_name = f"{data_motn.year} {calendar.month_name[data_motn.month].capitalize()}"
                                month_temp = period.strftime('%Y-%02m-%02d')

                                data = {
                                    "Month":  month_temp,
                                    "Name": name,
                                    "Number": number,
                                    "Pokaz": int(entry["ПоказаниеПредыдущее"].encode('latin1').decode('unicode-escape').replace(" ", "").replace("\xa0", "").replace(',', '.')),
                                    "Pokaz_prev": int(pokaz_prev),
                                    "Month_name": month_name,
                                    "ПриборУчета": entry["ПриборУчета"],
                                    "ПриборУчетаКод": entry["ПриборУчетаКод"]


                                }
                                added_data = data


                    else:
                        print(f"No Pribor {name_key} found.")
                    if not added_data:
                        temp_entry_list = current_pribor_data[0]["ПриборУчета"].split('/')
                        if len(temp_entry_list) > 2:
                            number = temp_entry_list[0] + '/' + temp_entry_list[1]
                            name = temp_entry_list[2]
                        else:
                            number, name = temp_entry_list
                        data_key_temp = data_motn - timedelta(days=data_motn.day)
                        month_key_temp = f"{data_key_temp.year} {calendar.month_name[data_key_temp.month].capitalize()}"
                        prev_month_data = formatted_data.get(month_key_temp, [])
                        month_name = f"{data_motn.year} {calendar.month_name[data_motn.month].capitalize()}"
                        pokaz_prev = 0
                        for i in prev_month_data:
                            if i["ПриборУчета"] == current_pribor_data[0]["ПриборУчета"]:
                                pokaz_prev = i["Pokaz"]


                        current_month = datetime.now().month

                        if current_month == data_motn.month:
                            month_temp = datetime.now().strftime('%Y-%m-%d')
                        else:
                            month_temp = data_motn.strftime('%Y-%02m') + "-01"
                        data = {
                            "Month":  month_temp,
                            "Name": name,
                            "Number": number,
                            "Pokaz": int(pokaz_prev),
                            "Pokaz_prev": int(pokaz_prev),
                            "Month_name": month_name,
                            "ПриборУчета": current_pribor_data[0]["ПриборУчета"],
                            "ПриборУчетаКод": entry["ПриборУчетаКод"]

                        }


                        added_data = data
                    if month_key not in formatted_data:
                        formatted_data.update({month_key: []})
                    formatted_data[month_key].append(added_data)

            context['priboru'] = {key: formatted_data[key] for key in reversed(formatted_data)}
            return context

    def post(self, request, *args, **kwargs):
        data = request.POST.get('data')
        if data:
            response_list = {'data': []}
            lich = self.request.session.get('lich')
            lich_kv = self.request.session.get('lich_name')
            json_data_list = json.loads(data)
            for one_schetchik in json_data_list:
                if float(one_schetchik["Pokaz"]) > 0:
                    yslyga_code = None
                    name_elem = one_schetchik['Name']
                    if name_elem == "Електроенергія":
                        yslyga_code = "000000016"
                    elif name_elem == "Холодна вода":
                        yslyga_code = "000000048"
                    elif name_elem == "Опалення":
                        yslyga_code = "000000009"
                    elif name_elem == "Гаряча вода":
                        yslyga_code = "000000044"
                    else:
                        print("Not found yslyga")
                        yslyga_code = "000000048"
                    data_elem = one_schetchik["Month_name"]
                    code_elem = one_schetchik["NumberCode"]
                    date_without_dashes = data_elem.replace("-", "")


                    #{'КодУслуги': '000000016', 'КодЗдания': '000000001', 'ОрганизацияКод': '00-000001', 'ОбъектУстановки': '12001', 'ОбъектУстановки2': 'кв. №   1', 'СтрокаДата': '20240229', 'КодПриборУчета': '000000001', 'ПоказаниеПредыдущее': '27295', 'Показание': '27902'}
                    data = {"КодУслуги": yslyga_code, "КодЗдания": "000000001", "ОрганизацияКод": "00-000001",
                            "ОбъектУстановки": lich, "ОбъектУстановки2": lich_kv,
                            "СтрокаДата": date_without_dashes, "КодПриборУчета": code_elem,
                            "ПоказаниеПредыдущее": one_schetchik["Pokaz_prev"], "Показание": one_schetchik["Pokaz"]}

                    response = osbb.post_schetchik(data)

                    if response:
                        response_list['data'].append({'success': True, "Name": name_elem + '/' + one_schetchik["Number"]})
                    else:
                        response_list['data'].append({'success': False, "Name": name_elem + '/' + one_schetchik["Number"]})

            return JsonResponse(response_list)
        return JsonResponse({'data': [{'success': False,  "Name": "Error"}]})



class SetLichView(LoginRequiredMixin, TemplateView):
    template_name = None  # Указываем None, чтобы TemplateView не пытался рендерить шаблон

    def post(self, request, *args, **kwargs):
        selected_value = request.POST.get('selected_value')
        selected_value_content = request.POST.get('selected_value_content')
        request.session['lich'] = selected_value
        request.session['lich_name'] = selected_value_content
        return JsonResponse({'status': 'success'})


class CarsView(LoginRequiredMixin, TemplateView):
    template_name = 'cars.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user

        lich = self.request.session.get('lich')

        lich_response = osbb.get_lich_user(self.request.user.username)
        if lich_response:
            result_dict = {}
            for item in lich_response:
                number = item["number"]
                name = item["name"]
                code = item["code"]
                if number in result_dict:
                    # Если запись существует, добавляем текущее имя к существующему значению
                    result_dict[number]["codes"].append(code)
                    result_dict[number]["names"].append(name)
                else:
                    # Если записи нет, создаем новую запись в словаре
                    result_dict[number] = {"codes": [code], "names": [name]}

            result_list = []

            for key, value in result_dict.items():
                kv_codes = [code for code in value['codes'] if 'кв.' in value['names'][value['codes'].index(code)]]
                result_list.append(
                    {"number": key, "codes": ', '.join(kv_codes[:1]), "names": ', '.join(value['names'])})

            context['lich'] = result_list
        if not lich:

                context['lich_selected'] = result_list[0]['codes']
                context['lich_selected_name'] = result_list[0]['names']
        else:
            context['lich_selected'] = lich
            context['lich_selected_name'] = self.request.session.get('lich_name')


        cars_response = osbb.get_cars_user(context['lich_selected'])
        if cars_response:

            owner = lich_response[0]['owner']
            owner_phone = lich_response[0]['owner_phone']
            for i in cars_response:
                i.update({'owner': owner, 'owner_phone': owner_phone})

            new_data = []
            for item in cars_response:
                nomera = item["НомерМашиноМеста"].split(", ")
                for nomer in nomera:
                    new_item = item.copy()  # Создаем копию исходного словаря
                    new_item["НомерМашиноМеста"] = nomer  # Заменяем номер машиноместа на текущий
                    new_data.append(new_item)
            context['cars'] = new_data
        return context

    def post(self, request, *args, **kwargs):

        data = request.POST.get('data')
        if data:

            lich = self.request.session.get('lich')
            response_cars_get = osbb.get_cars()

            grouped_data = {}
            for item in json.loads(data):
                vid = item["Вид"]
                nomer = item["НомерМашиноМеста"]
                if vid not in grouped_data:
                    grouped_data[vid] = [nomer]
                else:
                    grouped_data[vid].append(nomer)

            # Проходимся по словарю и объединяем номера машиномест через запятую
            cars_list = [{"Вид": vid, "НомерМашиноМеста": ", ".join(grouped_data[vid])} for vid in grouped_data]

            founded_dosc = []
            for car in response_cars_get:
                if car['Posted'] == True and car['ВидОперации'] == 'ИзменениеМашиноМест' and car['ЛицевойСчет']['Code'] == lich:
                    founded_dosc.append(car['Ref_Key'])

            for car in founded_dosc:
                osbb.delete_cars(car)


            data_json = {"Owner": self.request.user.username, "КодЗдания": "000000001", "ОрганизацияКод": "00-000001",
                    "ПарИмя": lich, "ПриборыМашины": cars_list}
            response = osbb.post_cars(data_json)
            if response:
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error'})
        data_new = request.POST.get('data_new')
        if data_new:
            cars_list = json.loads(data_new)
            new_post_data = cars_list.pop()

            lich = self.request.session.get('lich')
            data_lich = new_post_data.get('data_lich')
            if lich != data_lich:
                cars_response = osbb.get_cars_user(data_lich)
                if cars_response and len(cars_response) > 0:

                    cars_list = [{"НомерМашиноМеста": i['НомерМашиноМеста'], "Вид": i['ВидМашиноМеста']} for i in cars_response]
                else:
                    cars_list = []

            car_view = "Паркінг" if new_post_data.get('checkboxGroup1') == 'park' else 'Двір'

            cars_list.append({"НомерМашиноМеста": new_post_data.get('number-car'), "Вид": car_view})

            grouped_data = {}
            for item in cars_list:
                vid = item["Вид"]
                nomer = item["НомерМашиноМеста"]
                if vid not in grouped_data:
                    grouped_data[vid] = [nomer]
                else:
                    grouped_data[vid].append(nomer)

            # Проходимся по словарю и объединяем номера машиномест через запятую
            cars_list = [{"Вид": vid, "НомерМашиноМеста": ", ".join(grouped_data[vid])} for vid in grouped_data]

            response_cars_get = osbb.get_cars()
            founded_dosc = []
            for car in response_cars_get:
                if car['Posted'] == True and car['ВидОперации'] == 'ИзменениеМашиноМест' and car['ЛицевойСчет'][
                    'Code'] == data_lich:
                    founded_dosc.append(car['Ref_Key'])

            for car in founded_dosc:
                osbb.delete_cars(car)



            data_json = {"Owner": self.request.user.username, "КодЗдания": "000000001", "ОрганизацияКод": "00-000001",
                         "ПарИмя": data_lich, "ПриборыМашины": cars_list}
            response = osbb.post_cars(data_json)
            if response:
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error'})

        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(request.path)


class VoteView(LoginRequiredMixin, TemplateView):
     template_name = 'vote.html'


     def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['user'] = self.request.user

            lich = self.request.session.get('lich')

            lich_response = osbb.get_lich_user(self.request.user.username)
            if lich_response:
                result_dict = {}
                for item in lich_response:
                    number = item["number"]
                    name = item["name"]
                    code = item["code"]
                    if number in result_dict:
                        # Если запись существует, добавляем текущее имя к существующему значению
                        result_dict[number]["codes"].append(code)
                        result_dict[number]["names"].append(name)
                    else:
                        # Если записи нет, создаем новую запись в словаре
                        result_dict[number] = {"codes": [code], "names": [name]}

                result_list = []

                for key, value in result_dict.items():
                    kv_codes = [code for code in value['codes'] if 'кв.' in value['names'][value['codes'].index(code)]]
                    result_list.append(
                        {"number": key, "codes": ', '.join(kv_codes[:1]), "names": ', '.join(value['names'])})

                context['lich'] = result_list
            if not lich:

                context['lich_selected'] = result_list[0]['codes']
                context['lich_selected_name'] = result_list[0]['names']
            else:
                context['lich_selected'] = lich
                context['lich_selected_name'] = self.request.session.get('lich_name')

            votes_response = osbb.get_votes()
            votes_result_response = osbb.get_votes_result()
            if votes_response:
                poll_data = []
                for data_vote in votes_response:
                    number = data_vote.get('Number')
                    head_text = data_vote.get('ШапкаИнформационногоБюлетня')
                    try:
                        poll = Poll.objects.get(text=number + head_text)
                    except Poll.DoesNotExist:
                        # Запись не найдена, создаем новую
                        poll = Poll.objects.create(text=number + head_text)
                    result_votes = None
                    for i in votes_result_response:
                        if i['Вопрос'] == data_vote['ВопросГолосования']['Description']:
                            result_votes = i

                    # Общее количество ответов

                    # Выбираем поля для подсчета голосов
                    voting_fields = ["За", "Против", "Воздержался"]

                    # Вычисляем общее количество голосов
                    total_votes = sum(int(result_votes[field]) for field in voting_fields)

                    # Создаем список для хранения результатов
                    result_list = []

                    # Проходим по выбранным полям для подсчета голосов
                    for field in voting_fields:
                        # Преобразуем количество голосов в целое число
                        count = int(result_votes[field])

                        # Вычисляем процент голосов для текущего варианта
                        if total_votes > 0:
                            percentage = (count / total_votes) * 100
                        else:
                            percentage = 0.0

                        # Добавляем результат в список
                        result_list.append({'имя': field, 'варианты': count, 'проценты': percentage})

                    poll_dict = {"Poll_data": poll, "head_text": head_text,
                                 "ФормаГолос": data_vote['ФормаГолосования']['Description'],
                                 "Data": data_vote['Date'],
                                 "ВопросГолосования": data_vote['ВопросГолосования']['Description'],
                                 "РезультатГолосования": result_list}
                    poll_data.append(poll_dict)

            # all_polls = Poll.objects.all()
            # all_polls = all_polls.annotate(Count('vote')).order_by('-created_at')


            # paginator = Paginator(all_polls, 100)  # Show 6 contacts per page
            # page = request.GET.get('page')
            # polls = paginator.get_page(page)

            # get_dict_copy = request.GET.copy()
            # params = get_dict_copy.pop('page', True) and get_dict_copy.urlencode()

            sorted_data = sorted(poll_data, key=lambda x: x['Data'], reverse=True)
            last_poll = sorted_data[0]


            context = {
                "last_poll": last_poll,
                'polls': sorted_data[1:]
            }
            return context

     def post(self, request, *args, **kwargs):

            choice_id = json.loads(request.body.decode('utf-8')).get('choice_id')
            choice_id, poll_id = choice_id.split('_')
            poll = Poll.objects.get(id=poll_id)
            if not poll.user_can_vote(request.user):
                print("User already voted")
                return JsonResponse({'success': False, 'error_message': "Ви вже голосували в цьому опитуванні!"})


            if choice_id:

                votes_doc = osbb.get_votes_doc()
                finded_doc = None
                for i in votes_doc:
                    number = i['ДокументОснование'].get('Number')
                    head_text = i['ДокументОснование'].get('ШапкаИнформационногоБюлетня')

                    if number + head_text == poll.text:
                        finded_doc = i

                choice = Choice.objects.get(id=choice_id)

                prev_results = finded_doc['РезультатыГолосования']
                lich_code = self.request.session.get('lich')
                lich_response = osbb.get_lic_odata()
                lich_ref = None
                for i in lich_response:
                    if i['Code'] == str(lich_code):
                        lich_ref = i['Ref_Key']
                last_result = prev_results[-1]
                data = {
                    "LineNumber": str(int(last_result['LineNumber']) + 1),
                    "ВариантОтвета": choice.choice_text,
                    "ЛицевойСчет_Key": lich_ref,
                    "ОтветственныйВладелец_Key": "00000000-0000-0000-0000-000000000000"
                }
                for i in prev_results:
                    del i['Ref_Key']
                prev_results.append(data)

                if prev_results:
                    prev_results = {"РезультатыГолосования": prev_results}

                # Создаем пустой список для хранения словарей
                results = []

                # Проходим по результатам голосования и добавляем в список словари в нужном формате
                for result in prev_results['РезультатыГолосования']:
                    vote = result['ВариантОтвета']
                    results.append({'имя': vote, 'варианты': 1})

                # Собираем результаты в словарь, где ключ - имя варианта ответа, а значение - суммарное количество голосов
                votes_count = {}
                for result in results:
                    name = result['имя']
                    if name in votes_count:
                        votes_count[name] += 1
                    else:
                        votes_count[name] = result['варианты']

                choice = Choice.objects.get(id=choice_id)

                branches = dia.get_branches()
                current_branch = None
                for branch in branches['branches']:
                    if branch['name'] == 'ЖК Синій птах голосвування':
                        current_branch = branch
                        print("Select branch for DIA")
                        break
                offers = dia.get_offer(current_branch['_id'])
                current_offer = None
                head_offer = finded_doc['ДокументОснование'].get('ШапкаИнформационногоБюлетня')
                for offer in offers['offers']:
                    if offer['name'] == head_offer:
                        current_offer = offer
                        print("Select offer for DIA")
                        break

                if not current_offer:
                    print("Create offer for DIA")
                    current_offer = dia.post_offer(current_branch['_id'], head_offer)
                full_name = ''

                if request.user.last_name is not None:
                    full_name += request.user.last_name + ' '

                if request.user.first_name is not None:
                    full_name += request.user.first_name + ' '

                if request.user.middle_name is not None:
                    full_name += request.user.middle_name

                request_id = dia.hash_request_id()
                last_poll = {'head_text': head_offer,
                             'question': finded_doc['ВопросГолосования']['Description'],
                             'results': votes_count,
                             'user_name': full_name,
                             'user_answer': choice.choice_text}
                file_name = f"{head_offer}{datetime.now().timestamp()}.pdf"
                print("Prepare to craeate file")
                dia.create_dia_file(last_poll, file_name)
                file_hash = dia.calculate_file_hash(file_name)
                link = dia.post_dynamic(current_branch['_id'], current_offer['_id'], request_id, file_name, file_hash )
                if link:
                    try:
                        DIA_model.objects.create(poll=poll, request_id=request_id,  file_name=file_name,
                                       choice=choice,  user=self.request.user, lich_code=lich_code)

                    except Exception as e:
                        print(e)
                        return JsonResponse( {'success': False, 'error_message': "Помилка!"})
                    return JsonResponse({'success': True, 'qr_image_base64': link['deeplink']})

                return JsonResponse({'success': False, 'error_message': "Помилка!"})
            else:
                return JsonResponse({'success': False, 'error_message': "Не вибрано жодного варіанту!"})
            return JsonResponse({'success': False, 'error_message': "Помилка!"})





class ArchiveView(LoginRequiredMixin, TemplateView):
    template_name = 'archive.html'


class InfoView(LoginRequiredMixin, TemplateView):
    template_name = 'info.html'


class PaymentView(LoginRequiredMixin, TemplateView):
    template_name = 'payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user

        lich = self.request.session.get('lich')
        lich_response = osbb.get_lich_user(self.request.user.username)
        if lich_response:
            result_dict = {}
            for item in lich_response:
                number = item["number"]
                name = item["name"]
                code = item["code"]
                if number in result_dict:
                    # Если запись существует, добавляем текущее имя к существующему значению
                    result_dict[number]["codes"].append(code)
                    result_dict[number]["names"].append(name)
                else:
                    # Если записи нет, создаем новую запись в словаре
                    result_dict[number] = {"codes": [code], "names": [name]}

            result_list = []

            for key, value in result_dict.items():
                kv_codes = [code for code in value['codes'] if 'кв.' in value['names'][value['codes'].index(code)]]
                result_list.append(
                    {"number": key, "codes": ', '.join(kv_codes[:1]), "names": ', '.join(value['names'])})

            if not lich:
                context['lich_selected'] = result_list[0]['codes']
                context['lich_selected_name'] = result_list[0]['names']
            else:
                context['lich_selected'] = lich
                context['lich_selected_name'] = self.request.session.get('lich_name')

            try:
                selected_terminal = [i for i in lich_response if i['code'] == context['lich_selected']][0]['Комментарий']
            except Exception as e:
                selected_terminal = None

            context['selected_terminal'] = selected_terminal

            context["privat_url"] = f"https://next.privat24.ua/payments/form/%7B%22token%22%3A%22f12d8b187763a58e9de55ec6c5c02e2fp52n1tya%22%2C%22personalAccount%22%3A%22{selected_terminal}%22%7D"


            ostatok_response = osbb.get_ostatok_user(context['lich_selected'])
            if ostatok_response:
                ostatok_value = ostatok_response.get('ostatok', 0).encode('latin1').decode('unicode-escape')
                ostatok_value = ''.join(ostatok_value.split()).replace(',', '.')

                context['ostatok'] =  round(float(ostatok_value), 2) if float(ostatok_value) > 0 else 0
            return context

    def post(self, request, *args, **kwargs):
        terminal = request.POST.get('terminal')
        amount = request.POST.get('amount')
        if terminal:
            lich = self.request.session.get('lich')
            lich_kv = self.request.session.get('lich_name')
            html = liqpay.cnb_form({
                "action": "pay",
                "amount": amount,
                "currency": "UAH",
                "description": "description text",
                "order_id": terminal,
                "version": "3"
            })
            return JsonResponse({'status': 'success', 'data': html})
        return JsonResponse({'status': 'false'})

class DocsView(LoginRequiredMixin, TemplateView):
    template_name = 'docs.html'


class SupportView(LoginRequiredMixin, TemplateView):
    template_name = 'support.html'

    def post(self, request, *args, **kwargs):
        category = request.POST.get('category')
        description = request.POST.get('comments')
        if category and description:
            SupportTicket.objects.create(category=category, description=description, from_user=self.request.user.username)

            messages.success(request, _('Ваш тікет успішно відправлено.'))
        else:
            messages.error(request, 'Помилка під час надсилання форми. Будь ласка, заповніть усі поля.')

        return redirect('support')


class ChangeProfileView(LoginRequiredMixin, FormView):
    template_name = 'profile.html'
    form_class = ChangeProfileForm

    def get_initial(self):
        user = self.request.user
        initial = super().get_initial()



        response = osbb.get_user_by_username(user.username)
        if response:
            user_names = response.get('Description').split(' ')
            if len(user_names) == 3:
                initial['first_name'] = user_names[0]
                initial['last_name'] = user_names[1]
                initial['middle_name'] = user_names[2]
            else:
                initial['first_name'] = user_names[0]
                initial['last_name'] = user_names[1]

            initial['mobile'] = response.get('МобДляСайта')
            initial['email'] = response.get('ЕлектроннаяПочта')
            initial['address'] = user.address
            initial['profile_picture'] = user.profile_picture
        else:
            initial['first_name'] = user.first_name
            initial['last_name'] = user.last_name
            initial['middle_name'] = user.middle_name
            initial['mobile'] = user.mobile
            initial['email'] = user.email
            initial['address'] = user.address
            initial['profile_picture'] = user.profile_picture



        return initial

    def form_valid(self, form):
        user = self.request.user
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.middle_name = form.cleaned_data['middle_name']
        user.mobile = form.cleaned_data['mobile']
        user.email = form.cleaned_data['email']
        user.address = form.cleaned_data['address']
        user.profile_picture = form.cleaned_data['profile_picture']

        data = {
            "Description": f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']} {form.cleaned_data['middle_name']}",
            "МобДляСайта": form.cleaned_data['mobile'],
            "ЕлектроннаяПочта": form.cleaned_data['email'],
        }
        response = osbb.get_user_by_username(user.username)
        if response:
            osbb.patch_user(response['Ref_Key'], data)

        old_password = form.cleaned_data['old_password']
        new_password = form.cleaned_data['new_password']
        if len(old_password) > 0 and len(new_password) > 0:
            user_auth = authenticate(username=self.request.user.username, password=old_password)
            if user_auth:
                user.set_password(new_password)
                user.save()
                user = authenticate(username=self.request.user.username, password=new_password)
                login(self.request, user)
                update_session_auth_hash(self.request, user)
                if response:
                    data = {
                        "Пароль" : new_password
                    }
                    osbb.patch_user(response['Ref_Key'], data)


                messages.success(self.request, _('Пароль оновлено'))
            else:
                messages.error(self.request, str('Старий пароль невірний'))


        try:
            user.save()
            messages.success(self.request, _('Дані профілю успішно оновлено'))
        except Exception as e:
            messages.error(self.request, str(e))  # Выводим сообщение об ошибке

        return redirect('profile')

    def form_invalid(self, form):
        # Добавляем ошибку в контекст, чтобы отобразить её в шаблоне
        for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(self.request, f'Помилка при оновленні профілю для поля {field}: {error}')

        return super().form_invalid(form)


class GuestOnlyView(View):
    def dispatch(self, request, *args, **kwargs):
        # Redirect to the index page if the user already authenticated
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)

        return super().dispatch(request, *args, **kwargs)

from django.contrib.auth import get_user_model
class PasswordResetView(GuestOnlyView, FormView):
    template_name = 'password_reset.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['country_codes'] = country_codes
        return context

    @staticmethod
    def get_form_class(**kwargs):
        return ChangePasswordPhoneForm

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form, error='Неправильні дані'))

    def form_valid(self, form):

        phone_number = form.cleaned_data.get('phone')
        User = get_user_model()
        code = form.data.get('country_code').replace("+", "")
        phone = code + phone_number
        response_user = osbb.get_user_by_username(phone)
        if not response_user:
            return self.render_to_response(self.get_context_data(form=form,
                                                                 error='Такого користувача не знайдено'))
        ref_key = response_user.get('Ref_Key')
        try:
            user = User.objects.get(ref_key=ref_key)
        except User.DoesNotExist:
            return self.render_to_response(self.get_context_data(form=form,
                                                                 error='Такого користувача не знайдено'))


        code = ''.join(random.choices('0123456789', k=6))

        self.request.session['reset_code'] = code
        self.request.session['reset_user_ref'] = ref_key


        message = f'Ваш код для сброса пароля: {code}'
        response_sms = send_sms(phone, message)
        if response_sms:
            return redirect('verify_reset_code')
        else:
            return self.render_to_response(self.get_context_data(form=form,
                                                                      error="Помилка з смс-сервером"))


class VerifyResetCodeView(GuestOnlyView, FormView):
    template_name = 'verify_reset_code.html'

    @staticmethod
    def get_form_class(**kwargs):
        return ChangePasswordCodeForm

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form, error='Неправильні дані'))

    def form_valid(self, form):
        reset_code = form.cleaned_data['reset_code']
        stored_code = self.request.session.get('reset_code')
        if reset_code == stored_code:
            return redirect('reset_password')
        else:
            return self.render_to_response(self.get_context_data(form=form, error='Невірний код підтвердження'))


class ResetPasswordView(GuestOnlyView, FormView):
    template_name = 'reset_password.html'

    @staticmethod
    def get_form_class(**kwargs):
        return ChangePasswordConfirmForm

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form, error='Неправильні дані'))

    def form_valid(self, form):
        new_password = form.cleaned_data['new_password']
        confirm_password = form.cleaned_data['confirm_password']
        if new_password == confirm_password:
            User = get_user_model()
            reset_user_ref = self.request.session.get('reset_user_ref')
            try:
                user = User.objects.get(ref_key=reset_user_ref)
            except User.DoesNotExist:
                return self.render_to_response(self.get_context_data(form=form, error='Помилка'))


            data = {"Логин": user.username, "Пароль": new_password}
            response_update_password = osbb.patch_user(reset_user_ref, data)
            if response_update_password:
                user.set_password(new_password)
                user.save()
                # Optionally log the user in
                user = authenticate(username=user.username, password=new_password)
                if user is not None:
                    login(self.request, user)
                messages.success(self.request, 'Пароль успешно изменен')
                return redirect('home')
            else:
                return self.render_to_response(self.get_context_data(form=form, error='Помилка'))
        else:
            return self.render_to_response(self.get_context_data(form=form, error='Паролі не співпадають'))


class LogInView(GuestOnlyView, FormView):
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            background_photo = BackgroundModel.objects.filter(photo_type='login_background').first()
            context['background_photo_url'] = background_photo.photo.url
        except Exception as e:
            pass
        context['country_codes'] = country_codes
        return context

    @staticmethod
    def get_form_class(**kwargs):
        return SignInViaUsernameForm

    def form_valid(self, form):
        request = self.request

        # If the test cookie worked, go ahead and delete it since its no longer needed
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()


        login(request, form.user_cache)

        redirect_to = request.POST.get(REDIRECT_FIELD_NAME, request.GET.get(REDIRECT_FIELD_NAME))
        url_is_safe = is_safe_url(redirect_to, allowed_hosts=request.get_host(), require_https=request.is_secure())

        if url_is_safe:
            #try:
                #notify.send(self.request.user, recipient=self.request.user,
                #verb=f'Новий вхід {self.request.user.username}')
            #except Exception as e:
                #pass

            return redirect(redirect_to)

        return redirect(settings.LOGIN_REDIRECT_URL)

    def form_invalid(self, form):
        # Добавляем ошибку в контекст, чтобы отобразить её в шаблоне
        return self.render_to_response(self.get_context_data(form=form, error='Неправильні облікові дані для входу'))


class CustomLogoutMixin:

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        return response


class LogOutView(CustomLogoutMixin, BaseLogoutView):
    next_page = reverse_lazy('login')


@csrf_exempt
def execute_script(request):
    # Перевірка, чи існує параметр request_id
    try:
        request_id = request.GET.get('request_id')
        if not request_id:
            return JsonResponse({"error": "Unauthorized request"}, status=401)
        query_params = request.GET
        body_data = request.body

        # Получаем значение параметра request_id
        request_id = request.headers.get('X-Document-Request-Trace-Id')
        print("Successfully received a request from the DIA")

        current_vote_dia = DIA_model.objects.get(request_id = request_id)

        votes_doc = osbb.get_votes_doc()
        finded_doc = None
        for i in votes_doc:
            number = i['ДокументОснование'].get('Number')
            head_text = i['ДокументОснование'].get('ШапкаИнформационногоБюлетня')

            if number + head_text == current_vote_dia.poll.text:
                finded_doc = i



        prev_results = finded_doc['РезультатыГолосования']

        lich_response = osbb.get_lic_odata()
        lich_ref = None
        for i in lich_response:
            if i['Code'] == str(current_vote_dia.lich_code):
                lich_ref = i['Ref_Key']
        last_result = prev_results[-1]
        data = {
            "LineNumber": str(int(last_result['LineNumber']) + 1),
            "ВариантОтвета": current_vote_dia.choice.choice_text,
            "ЛицевойСчет_Key": lich_ref,
            "ОтветственныйВладелец_Key": "00000000-0000-0000-0000-000000000000"
        }
        for i in prev_results:
            del i['Ref_Key']
        prev_results.append(data)

        if prev_results:
            prev_results = {"РезультатыГолосования": prev_results}

        patch_response = osbb.patch_vote(finded_doc['Ref_Key'], prev_results)
        if patch_response:


            vote = Vote(user=current_vote_dia.user, poll=current_vote_dia.poll, choice=current_vote_dia.choice)
            vote.save()

            current_vote_dia.hash_file = body_data
            current_vote_dia.save()
            notify.send(current_vote_dia.user, recipient=current_vote_dia.user, verb=f'Ви успішно підтвердили голосування')

            print("Saved data for vote")
        else:
            print("Error in patch vote 1c")
    except Exception as e:
        print(f"Error in dia request {e}")
    return JsonResponse({"success": True}, status=200, safe=False)