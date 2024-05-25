# Добавляем путь к родительскому каталогу в sys.path
import os, sys
current_script_directory = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.join(current_script_directory, '..')
sys.path.append(parent_directory)

import os

import django
from django.conf import settings

settings_module = "backend.settings"  # Замените "your_project_name" на имя вашего Django проекта
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
django.setup()

from django.contrib.auth import get_user_model
# Получаем модель пользователя
User = get_user_model()
from django.core.files import File
import os

# Путь к новой аватарке
picture_path = 'Designer.jpg'

# Проверяем существование файла
if not os.path.exists(picture_path):
    print('The provided picture path does not exist')
else:
    # Открываем файл с аватаркой
    with open(picture_path, 'rb') as f:
        profile_picture = File(f)

        # Обновляем аватарку для каждого пользователя
        users = User.objects.all()
        for user in users:
            user.profile_picture.save(os.path.basename(picture_path), profile_picture, save=True)
            print(f'Updated profile picture for user: {user.username}')

    print('Successfully updated profile pictures for all users')