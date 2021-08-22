import requests
import urllib
from bs4 import BeautifulSoup
import glob
from urllib.request import Request, urlopen
from urllib.parse import urlparse
import re
import os

DATASET_URL = "https://ptgh.onego.ru/9006/"
url = Request(DATASET_URL)
html_page = urlopen(url)
soup = BeautifulSoup(html_page, "html.parser")
links = []
# нет селектора, поиск идет по всем тегам <a>
for item in soup.findAll('a'):
    links.append(item.get('href'))
for index, link in enumerate(links):    # кол-во итераций = кол-ву ссылок
    if (link.find('ismen_nov')) != -1:
        changes_schedule_link = str(link).replace(' ', '')
        changes_schedule = urlparse(changes_schedule_link)
        global NAME_OF_CHANGES_SCHEDULE_FILE
        NAME_OF_CHANGES_SCHEDULE_FILE = changes_schedule.path.replace('/', '')
        print(NAME_OF_CHANGES_SCHEDULE_FILE)
        continue        # переход к следующей итерации
    if re.search(r'РАСПИСАНИЕ.*\.xlsx', link):
        main_schedule_link = link
        main_schedule = urlparse(link)
        print(main_schedule)
        NAME_OF_MAIN_SCHEDULE_FILE = main_schedule.path.replace('/', '')
        print(NAME_OF_MAIN_SCHEDULE_FILE)

# import os
# for file in os.listdir():
# if os.path.isfile(file):
# pass #обработка каждого из файлов тут
#
# Если нужно обрабатывать определенную папку - укажите её адрес в аргументе listdir так:
# os.listdir(path_here)

file_list = glob.glob('*.xlsx')
print(file_list)
if not file_list:
    print('excel файлов нет')
else:
    for xlsx_file in file_list:
        if xlsx_file == NAME_OF_CHANGES_SCHEDULE_FILE or xlsx_file == NAME_OF_MAIN_SCHEDULE_FILE:
            print('нового расписания нет')
            break
        else:
            main_schedule_xlsx = requests.get(main_schedule_link)
            main_schedule_xlsx.encoding = '1251'
            # main_schedule_xlsx = urllib.request.urlopen(
            #     main_schedule).read()
            # Пример для 'https://bdt.spb.ru/афиша':
            # bdt = 'https://bdt.spb.ru/' + quote('афиша')
            #urllib.request.urlopen(bdt)
            f = open(NAME_OF_MAIN_SCHEDULE_FILE, "w")
            f.write(str(main_schedule_xlsx))
            f.close()
            print('Основное расписание обновлено')
            changes_schedule_xlsx = urllib.request.urlopen(
                changes_schedule_link).read()
            f = open(NAME_OF_CHANGES_SCHEDULE_FILE, "wb")
            f.write(changes_schedule_xlsx)
            f.close()
            print('Изменения к основному расписанию обновлены')
            new_file_list = glob.glob('*.xlsx')
            # for old_xlsx_file in new_file_list:
            #     print(old_xlsx_file)
            #     if old_xlsx_file != NAME_OF_CHANGES_SCHEDULE_FILE and xlsx_file == NAME_OF_MAIN_SCHEDULE_FILE:
            #         os.remove(old_xlsx_file)
            # for user in get_subsribed(db):
            #     try:
            #         context.bot.send_message(chat_id=user['chat_id'],
            #                                  text='Расписание обновлено')
            #     except Unauthorized:
            #         print(f"Пользователь заблокировал бота {user['chat_id']}")