from bs4 import BeautifulSoup
import glob
from urllib.request import Request, urlopen
import urllib.request
from urllib.parse import urlparse
import os.path
import schedule
import time


def working_with_files():
    print("I'm working...")
    DATASET_URL = "https://ptgh.onego.ru/9006/"
    url = Request(DATASET_URL)
    html_page = urlopen(url)
    soup = BeautifulSoup(html_page, "html.parser")
    link = []
    for item in soup.findAll('a'):
        link.append(item.get('href'))

    for index, elem in enumerate(link):
        if (elem.find('ismen_nov')) != -1:
            new_elem = urlparse(elem)
            print(new_elem)
            new_elem_replace = new_elem[2].replace('/', '')
            print(new_elem_replace)
            break

    file_list = glob.glob('*.xlsx')
    print(file_list)
    if not file_list:
        print('excel файлов нет')
    else:
        if file_list[0] == new_elem_replace:
            print('нового расписания нет')
            pass
        else:
            file_xlsx = urllib.request.urlopen(elem).read()
            f = open(new_elem_replace, "wb")
            f.write(file_xlsx)
            f.close()
            print('доступно новое расписание')
            # context.bot.send_message(chat_id=594500841, text='Доступно новое расписание')
    file_list = glob.glob('*.xlsx')
    for item in file_list:
        if item != new_elem_replace:
            os.remove(item)
working_with_files()

# schedule.every(10).seconds.do(working_with_files)
# while True:
#     schedule.run_pending()
#     time.sleep(1)
