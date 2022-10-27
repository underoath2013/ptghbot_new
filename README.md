# Russian
# Ptghbot
Тестовый бот<br />
Ознакомиться с функционалом и просмотреть работу -> @ptghbot

## Установка

1. Клонируйте репозиторий с github
2. Создайте виртуальное окружение
3. Установите зависимости командой `pip install -r requirements.txt`
4. Создайте файл `settings.py`
5. Впишите в settings.py переменные: токен вашего бота, адрес MongoDB
7. Запустите бота командой `python bot.py`

### Как работает бот?
Библиотека
https://python-telegram-bot.readthedocs.io

При помощи встроенного в библиотеку менеджера задач (JobQueue) запускает раз в заданный интервал (например 3600 сек.) времени функцию parsing_links_from_schedule_html_downloading_schedules().

parsing_links_from_schedule_html_downloading_schedules()
По заданной ссылке отслеживает появление нового расписания методом сравнения изменяемой  части ссылки с именем excel файлов, лежащих в папках changes_schedule и main_schedule.
Если на сервер загружается новый файл, часть ссылки меняется, загружается новый файл, старый файл удаляется, пользователи получают уведомление о доступности нового расписания. Дополнительно Изменения к расписанию сериализуются в pickle файл в папку changes_schedule, для быстрого обращения к распарсенным данным. 

Обработка excel файла расписания организована через библиотеку OpenpyXL, вызывается в функции def parsing_data().
Алгоритм парсинга хранится в system_functions.py

Пользователь нажимает кнопку Просмотреть изменения -> получает список дат, на которые доступно расписание -> выбирает дату -> выводится список групп -> выбирает нужную группу -> получает расписание для выбранной группы.

Дополнительный функционал: <br />
Скачивание основного расписания <br />
Скачивание изменений к расписанию <br />
Вывод картинки звонков <br />
Вывод информации о боте <br />

Данные о пользователях хранятся в MongoDB по схеме: <br />
"user_id" <br />
"first_name" <br />
"last_name" <br />
"username" <br />
"chat_id" <br />
'subscribed' - подписка на рассылку о появлении нового расписания

# English
# Ptghbot
Test bot<br />
Check out the functionality and view the work -> @ptghbot

## Installation

1. Clone the repository from github
2. Create a virtual environment
3. Install dependencies with `pip install -r requirements.txt`
4. Create a file `settings.py`
5. Enter variables in settings.py: your bot token, MongoDB address
7. Run the bot with the command `python bot.py`

### How does the bot work?
Library
https://python-telegram-bot.readthedocs.io

With the help of the task manager (JobQueue) built into the library, it launches the parsing_links_from_schedule_html_downloading_schedules() function once at a specified interval (for example, 3600 seconds).

parsing_links_from_schedule_html_downloading_schedules()
Using the given link, it monitors the appearance of a new schedule by comparing the changed part of the link with the name of excel files located in the changes_schedule and main_schedule folders.
If a new file is uploaded to the server, part of the link changes, a new file is uploaded, the old file is deleted, users are notified that a new schedule is available. Additionally Changes to the schedule are serialized into a pickle file in the changes_schedule folder, for quick access to the parsed data.

The processing of the excel schedule file is organized through the OpenpyXL library, it is called in the def parsing_data () function.
The parsing algorithm is stored in system_functions.py

The user clicks the View Changes button -> gets a list of dates for which a schedule is available -> selects a date -> a list of groups is displayed -> selects the desired group -> gets the schedule for the selected group.

Additional functionality: <br />
Downloading the main schedule <br />
Downloading changes to the schedule <br />
Call picture output <br />
Displaying information about the bot <br />

User data is stored in MongoDB according to the scheme: <br />
"user_id" <br />
"first_name" <br />
"last_name" <br />
username <br />
"chat_id" <br />
'subscribed' - subscription to a newsletter about a new schedule
