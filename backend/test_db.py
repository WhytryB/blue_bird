
import pyodbc

# Замените значения переменных на ваши данные
server = 'osbb.tais-dtb.com,48807'
username = 'osbb\\Fedorov'
password = 'tbWGeps0h5'

# Строка подключения
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};Server={server};UID={username};PWD={password}'

try:
    # Подключение к серверу 1C
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()

    # Получение списка баз данных
    cursor.execute("SELECT NAME FROM INFORMATIONREGISTERS.RDB$DATABASE")
    rows = cursor.fetchall()

    # Вывод списка баз данных
    print('Доступные базы данных:')
    for row in rows:
        print(row[0])

    # Закрытие соединения
    connection.close()

except pyodbc.Error as e:
    print(f'Ошибка подключения к серверу 1C: {e}')