import requests
from bs4 import BeautifulSoup

# Отправляем GET-запрос к странице с кодами стран
url = 'https://countrycode.org/'
response = requests.get(url)

# Проверяем успешность запроса
if response.status_code == 200:
    # Используем BeautifulSoup для парсинга HTML-страницы
    soup = BeautifulSoup(response.text, 'html.parser')

    # Находим таблицу с кодами стран
    table = soup.find('table', class_='table table-hover table-striped main-table')

    # Извлекаем строки таблицы
    rows = table.find_all('tr')
    result = []

    # Проходим по каждой строке таблицы
    for row in rows:
        # Извлекаем название страны и её код ISO
        cells = row.find_all('td')
        if len(cells) >= 2:
            country_name = cells[1].text.strip().split(',')[0]
            iso_code = cells[2].text.strip().split('/')[0].strip()
            print(f"{country_name}: {iso_code}")
            result.append({"name": iso_code, "code": f"+{country_name}"})

else:
    print('Ошибка при получении данных с сайта')

print("d")