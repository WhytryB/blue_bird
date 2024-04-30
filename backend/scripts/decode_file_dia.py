import base64

def decode_base64_to_file(base64_string, output_file_path):
    # Декодируем строку base64 обратно в бинарные данные
    decoded_data = base64.b64decode(base64_string)
    # Записываем декодированные данные в файл
    with open(output_file_path, "wb") as output_file:
        output_file.write(decoded_data)
    print("Файл успешно восстановлен.")

# Пример использования функции
base64_string = "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"  # Ваша строка base64
output_file_path = "restored_file.pdf"  # Путь, куда нужно сохранить восстановленный файл
decode_base64_to_file(base64_string, output_file_path)