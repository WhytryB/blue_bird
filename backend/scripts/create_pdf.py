# -*- coding: utf-8 -*-


import jinja2
import pdfkit


# pdfkit is just a wrapper for whktmltopdf. you need to install wkhtml and have it on the path
# alternatively, you can move wkhtmltoimage.exe, wkhtmltopdf.exe and wkhtmltox.dll into the working directory

# Create some data


def number_to_words_uk(n, cents=False):
    """
    Функция преобразует число в текст на украинском языке.
    """
    units = ['', 'один', 'два', 'три', 'чотири', "п'ять", 'шість', 'сім', 'вісім', 'дев`ять']
    units22 = ['', 'одна', 'дві', 'три', 'чотири', "п'ять", 'шість', 'сім', 'вісім', 'дев`ять']
    teens = ['', 'одинадцять', 'дванадцять', 'тринадцять', 'чотирнадцять', "п'ятнадцять", 'шістнадцять', 'сімнадцять',
             'вісімнадцять', 'дев`ятнадцять']
    tens = ['', '', 'двадцять', 'тридцять', 'сорок', "п'ятдесят", 'шістдесят', 'сімдесят', 'вісімдесят', 'дев`яносто']
    hundreds = ['', 'сто', 'двісті', 'триста', 'чотириста', "п'ятьсот", 'шістьсот', 'сімсот', 'вісімсот', 'дев`ятьсот']
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
env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))
template = env.get_template("tableTemplate.html")
# pass df, title, message to the template.
raschet = [{'month': '2024-03', 'month_oplata': 7649.26, 'month_dolg': 2768.14, 'month_nachislenie': 2768.14, 'services': [{'единица': 'кв.м.', 'тариф': 2.5, 'оплата': 415.75, 'нарах': 415.75, 'quantity_narah': 166.3, 'name': 'Утримання котельні  (абонплата впродовж року)', 'долг': 415.75}, {'единица': 'КВт/год', 'тариф': 2.64, 'оплата': 3896.64, 'нарах': 0, 'quantity_narah': 0, 'name': 'Електроенергія по приладам обліку', 'долг': 0}, {'единица': 'Чел.', 'тариф': 0.34, 'оплата': 56.54, 'нарах': 56.54, 'quantity_narah': 166.3, 'name': 'Вивезення ТПВ', 'долг': 56.54}, {'единица': 'куб.м.', 'тариф': 35.16, 'оплата': 984.48, 'нарах': 0, 'quantity_narah': 0, 'name': 'Холодне водопостачання по приладах обліку', 'долг': 0}, {'единица': 'кв.м.', 'тариф': 8.35, 'оплата': 1388.61, 'нарах': 1388.61, 'quantity_narah': 166.3, 'name': 'УБПТ (Утримання будинку і прибудинкової території)', 'долг': 1388.61}, {'единица': 'шт.', 'тариф': 205, 'оплата': 410.0, 'нарах': 205.0, 'quantity_narah': 1.0, 'name': 'Паркінг', 'долг': 205.0}, {'единица': 'Грн.', 'тариф': 0, 'оплата': 181.27, 'нарах': 181.27, 'quantity_narah': 166.3, 'name': 'Додаткові', 'долг': 181.27}, {'единица': 'Грн.', 'тариф': 1.9, 'оплата': 315.97, 'нарах': 315.97, 'quantity_narah': 166.3, 'name': 'Охорона', 'долг': 315.97}, {'единица': 'Грн.', 'тариф': 0, 'оплата': 0, 'нарах': 205.0, 'quantity_narah': 1.0, 'name': 'Борги минулих періодів', 'долг': 205.0}], 'month_name': '2024 Березня', 'second_month_name': 'Березня 2024'}]
kv_name = "Кравець Анастасія Володимирівна (5А)"
kv_ulica = "провулок Обсерваторний, будинок 2/6, кв. 5-А; мм. 44;"
kv_nomer = "215717"
kv_data = "02.2024"
kv_summa = "7 649,26"
amount = 7629.26
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

kv_data = {"kv_name": kv_name, "kv_ulica":kv_ulica, "kv_nomer": kv_nomer, "kv_data": kv_data, "kv_summa": kv_summa, "amount_in_words":amount_in_words }

html_out = template.render(raschet=raschet,
                           kv_data=kv_data)
options = {
  "enable-local-file-access": None
}

# write the html to file
with open("output.html", 'wb') as file_:
    file_.write(html_out.encode("utf-8"))

# write the pdf to file
pdfkit.from_string(html_out, output_path="output.pdf", css=["template.css"], options=options)
# # Данные для таблицы
# data = [
#     ['No', 'Найменування', 'Од.Вим.', 'Знач.', '02.2024', 'Тариф', 'Станом на', '01.02.2024', 'Оплата', 'Нарах.', '02.2024', 'Залік', 'Станом на', '29.02.2024', 'Долг', 'Перепл.', 'Долг', 'Перепл.'],
#     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
#     ['1', 'УБПТ (kv.1) (кв. 5-А)', 'кв.м.', '166,3000', '8,35', '1', '388,61', '1', '388,61', '1', '388,61', '0,00', '1', '388,61', '', ''],
#     ['2', 'Кладові (kl)', 'кв.м.', '0,0000', '5,00', '0,00', '0,00', '0,00', '0,00', '0,00', '0,00', '', ''],
#     ['3', 'Парковка (mm.1) (мм. 44)', 'Шт', '1,0000', '205,00', '205,00', '205,00', '205,00', '0,00', '205,00', '', ''],
#     ['4', 'Парковка (mm.2) (мм. 10)', 'Шт', '1,0000', '205,00', '205,00', '205,00', '205,00', '0,00', '205,00', '', ''],
#     ['5', 'Вивіз сміття (gb.1) (кв. 5-А)', 'Чел', '166,3000', '0,34', '56,54', '56,54', '56,54', '0,00', '56,54', '', ''],
#     ['6', 'Холодна вода сч. 1210006569, 254-226=28 куб.м.', 'куб.м.', '28,0000', '35,16', '0,00', '984,48', '0,00', '984,48', '', ''],
#     ['7', 'Електроенергія сч. 7513097000284, 99842-98366=1476 КВт/час', 'КВт/час', '1476,0000', '2,64', '4 942,08', '4 942,08', '3 896,64', '0,00', '3 896,64', '', ''],
#     ['8', 'Утримання котельні (ct.1) кв. 5-А', 'кв.м.', '166,3000', '2,50', '415,75', '415,75', '415,75', '0,00', '415,75', '', ''],
#     ['9', 'Охорона (кв. 5-А)', 'Грн.', '166,3000', '1,90', '315,97', '315,97', '315,97', '0,00', '315,97', '', ''],
#     ['10', 'Нерегулярні витрати', 'Грн.', '0,0000', '0,00', '0,00', '0,00', '0,00', '0,00', '0,00', '', ''],
#     ['11', 'Послугі з налаштування автоматичного доступу', 'Грн.', '0,0000', '0,00', '0,00', '0,00', '0,00', '0,00', '0,00', '', ''],
#     ['12', 'Внески до цільового фонду на придбання дизельгенератора', 'Грн.', '166,3000', '1,09', '181,27', '181,27', '181,27', '0,00', '181,27', '', ''],
#     ['13', 'Внески на дизельне пальне', 'Грн.', '166,3000', '0,00', '0,00', '0,00', '0,00', '0,00', '0,00', '', ''],
#     ['14', 'Перенесення боргів або переплат (kp)', 'Грн.', '0,0000', '0,00', '0,00', '0,00', '0,00', '0,00', '0,00', '', ''],
#     ['Всего', '', '', '', '7 710,22', '7 710,22', '7 649,26', '0,00', '7 649,26', '', ''],
# ]
#
# # Создаем текстовую строку для данных после 'До cплати:'
# additional_text = """
# До cплати: 7 649,26 сiм тисяч шiстьсот сорок дев'ять гривень, 26 коп.
# Призначення платежу: Комунальні послуги згідно о/р 215717
# Реквізити для оплати: ОСББ «Синій птах» код ЕДРПОУ 36795440, банк АБ "Приват банк" р/р UA613052990000026000044903898
# Оплату за рахунком виконувати до 29 числа поточного місяця в будь-якому банку
# Відвідайте особистий кабінет https://o26.osbb.od.ua логин 12006 пароль qfoj07f4. Пароль можно змініти в кабінеті. Будь ласка, заповніть в кабинеті контактні EMail та
# """
#
# # Создаем PDF файл
# pdf_filename = "invoice.pdf"
# doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
#
# # Создаем таблицу
# table = Table(data)
#
# # Назначаем стиль для таблицы
# style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Times-Roman'),
#                     ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                     ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
#                     ('GRID', (0, 0), (-1, -1), 1, colors.black)])
# table.setStyle(style)
#
# # Добавляем таблицу в документ
# elements = [table]
#
# # Добавляем текстовую строку после таблицы
# additional_text_paragraph = Paragraph(additional_text, ParagraphStyle(name='Normal'))
# elements.append(additional_text_paragraph)
#
# # Строим документ
# doc.build(elements)