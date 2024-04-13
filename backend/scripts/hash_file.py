import hashlib
import base64

def calculate_file_hash(file_path):
    # Открываем файл для чтения в бинарном режиме
    with open(file_path, "rb") as file:
        # Вычисляем хеш файла с использованием SHA256
        file_hash = hashlib.sha256(file.read()).digest()
        # Кодируем хеш в base64 и возвращаем как строку
        return base64.b64encode(file_hash).decode()

# Пример использования функции
file_path = "output.pdf"  # Путь к вашему файлу
file_hash_base64 = calculate_file_hash(file_path)
print("Хеш файла в формате base64:", file_hash_base64)