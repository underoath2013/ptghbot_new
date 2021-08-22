from bs4 import BeautifulSoup
from db import db, get_or_create_user, subscribe_user, unsubscribe_user, \
    get_subsribed
import glob
import logging
import requests
import openpyxl
import os.path
from random import choice
import re
import settings
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, ConversationHandler, \
    MessageHandler, Filters
from telegram.error import BadRequest, NetworkError, Unauthorized
from urllib.request import Request, urlopen
from urllib.parse import urlparse


logging.basicConfig(
    filename="bot.log", level=logging.INFO, format=
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def bot_commands(update, context):
    """ Доступные команды для работы с ботом """
    update.message.reply_text("/start - старт бота\n/subscribe - "
                              "получать уведомление о новом расписании\n"
                              "/unsubscribe - отписаться от уведомлений\n"
                              "автор бота @drbrch,"
                              " принимаю в лс предложения/замечания")


def main_keyboard():
    """ Клавиатура главного меню """
    return ReplyKeyboardMarkup(
        [['Скачать основное', 'Скачать изменения'], ['Просмотреть изменения'],
         ['Команды бота', 'Звонки']], resize_keyboard=True
    )


def subscribe(update, context):
    """ При вызове этой функции пользователь подписывается на рассылку
    уведомлений """
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    subscribe_user(db, user)
    update.message.reply_text('Уведомления о новом расписании подключены')


def unsubscribe(update, context):
    """ При вызове этой функции пользователь отписывается от рассылки
        уведомлений """
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    unsubscribe_user(db, user)
    update.message.reply_text('Уведомления о новом расписании отключены')


def parsing_links_from_schedule_html(context):
    """ Парсит страницу DATASET_URL, ищет ссылку на Изменения к основному
     расписанию, вызывает функцию скачивания downloading_schedules, передавая
       в нее параметры, необходимые для скачивания Изменений.
        Ищет ссылку на Основное расписание, вызывает функцию скачивания
        downloading_schedules, передавая в нее параметры, необходимые для
        скачивания Основного """
    print('*** Start parsing ***')
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
            changes_schedule_link = link
            changes_schedule = urlparse(changes_schedule_link)
            global NAME_OF_CHANGES_SCHEDULE_FILE
            NAME_OF_CHANGES_SCHEDULE_FILE = changes_schedule.path.replace(
                '/', '')
            print(NAME_OF_CHANGES_SCHEDULE_FILE)
            # передаем ссылку по которой качать, название папки,
            # имя скачиваемого файла, context
            downloading_schedules(
                changes_schedule_link, 'Изменения к расписанию',
                                  NAME_OF_CHANGES_SCHEDULE_FILE, context
            )
            continue        # переход к следующей итерации
        if re.search(r'РАСПИСАНИЕ.*\.xlsx', link):
            main_schedule_link = link
            main_schedule = urlparse(main_schedule_link)
            global NAME_OF_MAIN_SCHEDULE_FILE
            NAME_OF_MAIN_SCHEDULE_FILE = main_schedule.path.replace('/', '')
            print(NAME_OF_MAIN_SCHEDULE_FILE)
            # передаем ссылку по которой качать, название папки,
            # имя скачиваемого файла, context
            downloading_schedules(
                main_schedule_link, 'Основное расписание',
                                  NAME_OF_MAIN_SCHEDULE_FILE, context
            )


def downloading_schedules(
        schedule_link, schedule_folder, name_of_schedule_file, context):
    """ Принимает ссылку по которой качать, название папки,
     имя скачиваемого файла, context. Если папка пустая: качает
      Измения/Основное. Еще если: имя файла в папке с именем не совпадает с
      именем полученным при парсинге файла, качает файл и отсылает уведомления
      подписанным на уведомления пользователям """
    if len(os.listdir(schedule_folder)) == 0:   # listdir возвращает список
        schedule_xlsx = requests.get(schedule_link)
        f = open(schedule_folder + '/' + name_of_schedule_file, "wb")
        f.write(schedule_xlsx.content)  # записывает content из get запроса
        f.close()
        print(f'Расписание скачано в {schedule_folder}')
    elif os.listdir(schedule_folder)[0] != name_of_schedule_file:
        os.remove(schedule_folder + '/' + os.listdir(schedule_folder)[0])
        schedule_xlsx = requests.get(schedule_link)
        f = open(schedule_folder + '/' + name_of_schedule_file, "wb")
        f.write(schedule_xlsx.content)  # записывает content из get запроса
        f.close()
        print(f'Расписание обновлено в {schedule_folder}')
        for user in get_subsribed(db):
            try:
                context.bot.send_message(chat_id=user['chat_id'],
                                         text=f'{schedule_folder} обновлено')
            except Unauthorized:
                print(f"Пользователь {user['chat_id']} заблокировал бота")


def greet_user(update, context):
    """ Приветствует пользователя, выводит основную клавиатуру """
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    print("Вызван /start")
    update.message.reply_text("Привет, чтобы узнать расписание нажми кнопку\n"
                              "Уведомления об обновлении расписания\n"
                              "можно подключить в 'Команды бота'",
                              reply_markup=main_keyboard())


# chat_id = update.effective_chat.id - получить chat.id текущего пользователя


def show_rings(update, context):
    """ Выводит список звонков. Также будет выводить в случайном порядке
     любые jpeg файлы в каталоге images """
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    rings_list = glob.glob('images/rings*.jp*g')
    rings_pic_filename = choice(rings_list)
    context.bot.send_photo(chat_id=user['chat_id'],
                           photo=open(rings_pic_filename, 'rb'),
                           reply_markup=main_keyboard())


def dialog_start(update, context):
    book = openpyxl.open(
        'Изменения к расписанию/' + NAME_OF_CHANGES_SCHEDULE_FILE,
        read_only=True
    )
    my_keyboard = ReplyKeyboardMarkup([book.sheetnames], resize_keyboard=True)
    update.message.reply_text(
        "Изменения к расписанию занятий Корпус 1 (ул. Мурманская, д. 30)\n"
        "выберите дату:",
        reply_markup=my_keyboard)
    return "step_one"


def parsing_changes_xlsx(sheet):
    """  Обрабатывает excel файл с изменениями к расписанию """
    schedule = []
    for row in range(1, sheet.max_row):
        a_column = sheet[row][0].value
        if a_column is None:
            a_column = ''
        c_column = sheet[row][2].value
        if c_column is None or c_column == 'ауд.':
            c_column = ''
        b_column = sheet[row][1].value
        if b_column is None:
            continue
        else:
            b_column_split = ' '.join(b_column.split())
            result_abc = str(a_column) + str(b_column_split) + str(c_column)
            schedule.append(result_abc)
    for row in range(1, sheet.max_row):
        e_column = sheet[row][4].value
        if e_column is None:
            e_column = ''
        g_column = sheet[row][6].value
        if g_column is None or g_column == 'ауд.':
            g_column = ''
        f_column = sheet[row][5].value
        if f_column is None:
            continue
        else:
            f_column_split = ' '.join(f_column.split())
            result_efg = str(e_column) + str(f_column_split) + str(g_column)
            schedule.append(result_efg)
    return schedule


def choose_sheet(update, context):
    """ Парсит по именам группы расписание на выбранную пользователем дату,
    формирует словарь dict_groups и записывает его во встроенный словарь
    context.user_data, выводит списко групп пользователю """
    book = openpyxl.open(
        'Изменения к расписанию/' + NAME_OF_CHANGES_SCHEDULE_FILE,
        read_only=True
    )
    user_text = update.message.text
    context.user_data["dialog"] = {"sheet": user_text}
    sheet = book[context.user_data["dialog"]["sheet"]]
    parsed_schedule = parsing_changes_xlsx(sheet)
    groups = re.compile(
        r'(БД 12)|(БД 22)|(ИС 11)|(ИС 21)|(ИС 31)|(В 01)|(В 21)|(М 01)|(ПД 12)|'
        r'(ПД 13)|(ПД 22)|(ПД 23)|(ПД 24)|(ПД 32)|(ПД 33)|(ПД 34)|(ПСО 11)|'
        r'(ПСО 12)|(ПСО 21)|(ПСО 22)|(ПСО 31)|(ПСО 32)|(Т 11)|(Т 21)|(Т 31)|'
        r'(УД 01)|(УД 11)|(УД 21)|(УД 31)|(Э 12)|(Э 22)')
    idx1 = [i for i, item in enumerate(parsed_schedule) if
            re.search(groups, item)]
    dict_groups = {}
    for i in range(len(idx1) - 1):
        slices = parsed_schedule[idx1[i]:idx1[i + 1]]
        dict_groups[slices[0]] = slices[1:]
    try:
        last_slice = parsed_schedule[idx1[-1]:]
    except IndexError:
        update.message.reply_text("На этот день ничего нет",
                                  reply_markup=main_keyboard())
        return ConversationHandler.END
    dict_groups[last_slice[0]] = last_slice[1:]
    context.user_data["dict_groups"] = dict_groups
    groups_list = list(dict_groups.keys())
    n = 4
    group_names = [groups_list[i * n:(i + 1) * n] for i in
                   range((len(groups_list) + n - 1) // n)]
    my_keyboard = ReplyKeyboardMarkup(group_names, resize_keyboard=True)
    update.message.reply_text("Выберите группу:", reply_markup=my_keyboard)
    return "step_two"


def print_schedule(update, context):
    """ Печатает расписание для выбранной пользователем группы """
    context.user_data["dialog"]["group"] = update.message.text
    schedule_of_selected_group = \
        context.user_data["dict_groups"][context.user_data["dialog"]["group"]]
    # context.user_data.clear() позволяет очищать словарь context.user_data
    if len(schedule_of_selected_group) > 0:
        update.message.reply_text(
            str(schedule_of_selected_group).replace(
                ',', '\n').replace('[', '').replace(']', '').replace("'", ""),
            reply_markup=main_keyboard())
    else:
        update.message.reply_text("Удачи!", reply_markup=main_keyboard())
    return ConversationHandler.END


def main():
    mybot = Updater(settings.API_KEY, use_context=True)
    jq = mybot.job_queue
    # раз в заданный период и при старте бота запускаем функцию
    # downloading_and_comparing_xlsx_schedules
    jq.run_repeating(parsing_links_from_schedule_html,
                     interval=60, first=1)
    dp = mybot.dispatcher
    # начало диалога с пользователем
    dialog = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^([Пп]росмотреть изменения)$'),
                           dialog_start)
        ],
        states={
            "step_one": [MessageHandler(
                Filters.regex('\d\d.\d\d'),
                choose_sheet)],
            "step_two": [MessageHandler(Filters.regex(
                '(([ЭМТВ].[0-4][0-4])|([ЭМТВ].[0-4])|([БУИП][ДС].[0-4][0-4]|'
                '[ИБПУ][СД].[0-4])|([П][С][О].[0-4][0-4])|([ВМ][0-4]|'
                '[У][Д][0-4]))'), print_schedule)]
        },
        fallbacks=[]
    )
    dp.add_handler(dialog)
    dp.add_handler(CommandHandler('subscribe', subscribe))
    dp.add_handler(CommandHandler('unsubscribe', unsubscribe))
    dp.add_handler(CommandHandler('show_rings', show_rings))
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(MessageHandler(Filters.regex('^([Зз]вонки)$'), show_rings))
    dp.add_handler(
        MessageHandler(Filters.regex('^([Кк]оманды бота)$'), bot_commands))
    logging.info("bot started")
    mybot.start_polling()
    mybot.idle()


if __name__ == "__main__":
    main()
