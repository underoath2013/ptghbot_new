# Ptghbot
Это бот для Telegram, для вывода расписания учебного заведения

## Установка

1. Клонируйте репозиторий с github
2. Создайте виртуальное окружение
3. Установите зависимости командой `pip install -r requirements.txt`
4. Создайте файл `settings.py`
5. Впишите в settings.py переменные:
6. Proxy можно не использовать с 15.06.2020 Telegram в РФ разблокирован
```
API_KEY = "API -ключ бота"
PROXY_URL = "URL socks5-прокси"
PROXY_USERNAME = "Username для авторизации на прокси"
PROXY_PASSWORD = "Пароль  для авторизации на прокси"
USER_EMOJI = [':smiley_cat:', ':panda_face:', ':dog:', ':dollar:', ':bowtie:', ':flushed:', ':smiley:', ':wink:']
``` 
7. Запустите бота командой `python bot.py`