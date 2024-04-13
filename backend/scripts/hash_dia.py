import hashlib
import base64
import uuid

# Генерируем UUIDv4
request_id = uuid.uuid4()

# Преобразуем UUIDv4 в строку
request_id_str = str(request_id)

# Вычисляем хэш с помощью алгоритма SHA256
hash_object = hashlib.sha256(request_id_str.encode())
hash_value = hash_object.digest()

# Преобразуем полученное хэш-значение в формат base64
base64_hash_value = base64.b64encode(hash_value).decode()

print(base64_hash_value)