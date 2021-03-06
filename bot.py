import logging
import glob
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
import openpyxl
import settings
import re
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import urllib.request
from urllib.parse import urlparse
import os.path
from random import choice
from db import db, get_or_create_user, subscribe_user, unsubscribe_user, get_subsribed

logging.basicConfig(filename="bot.log", level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def bot_commands(update, context):
    update.message.reply_text("/start - старт бота\n/subscribe - получать уведомление о новом расписании\n/unsubscribe - отписаться от уведомлений\nавтор бота @drbrch, принимаю в лс предложения/замечания")


def subscribe(update, context):
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    subscribe_user(db, user)
    update.message.reply_text('Уведомления о новом расписании подключены')


def unsubscribe(update, context):
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    unsubscribe_user(db, user)
    update.message.reply_text('Уведомления о новом расписании отключены')


def working_with_files(context):
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
            global new_elem_replace
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
            print('Расписание обновлено')
            for user in get_subsribed(db):
                context.bot.send_message(chat_id=user['chat_id'], text='Расписание обновлено')
    file_list = glob.glob('*.xlsx')
    for item in file_list:
        print(item)
        if item != new_elem_replace:
            os.remove(item)


def greet_user(update, context):
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    print("Вызван /start")
    my_keyboard = ReplyKeyboardMarkup([['Расписание'], ['Команды бота'], ['Звонки']], resize_keyboard=True)
    update.message.reply_text("Привет, чтобы узнать расписание нажми кнопку\nУведомления можно подключить в 'Команды бота'", reply_markup=my_keyboard)


def show_rings(update, context):
    user = get_or_create_user(db, update.effective_user, update.message.chat.id)
    rings_list = glob.glob('images/rings*.jp*g')
    rings_pic_filename = choice(rings_list)
    #chat_id = update.effective_chat.id
    my_keyboard = ReplyKeyboardMarkup([['Расписание'], ['Команды бота'], ['Звонки']], resize_keyboard=True)
    context.bot.send_photo(chat_id=user['chat_id'], photo = open(rings_pic_filename, 'rb'), reply_markup = my_keyboard)


def dialog_start(update, context):
    book = openpyxl.open(new_elem_replace, read_only=True)
    my_keyboard = ReplyKeyboardMarkup([book.sheetnames], resize_keyboard=True)
    update.message.reply_text("Изменения к расписанию занятий Корпус 1 (ул. Мурманская, д. 30)\nвыберите дату:", reply_markup=my_keyboard)
    return "step_one"


def choose_sheet(update, context):
    book = openpyxl.open(new_elem_replace, read_only=True)
    user_text = update.message.text
    context.user_data["dialog"] = {"sheet": user_text}
    sheet = book[context.user_data["dialog"]["sheet"]]
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
    groups = re.compile(r'(БД 12)|(БД 22)|(ИС 11)|(ИС 21)|(ИС 31)|(В 01)|(В 21)|(М 01)|(ПД 12)|(ПД 13)|(ПД 22)|(ПД 23)|(ПД 24)|(ПД 32)|(ПД 33)|(ПД 34)|(ПСО 11)|(ПСО 12)|(ПСО 21)|(ПСО 22)|(ПСО 31)|(ПСО 32)|(Т 11)|(Т 21)|(Т 31)|(УД 01)|(УД 11)|(УД 21)|(УД 31)|(Э 12)|(Э 22)')
    idx1 = [i for i, item in enumerate(schedule) if re.search(groups, item)]
    dict_groups = {}
    for i in range(len(idx1)-1):
        slices = schedule[idx1[i]:idx1[i+1]]
        dict_groups[slices[0]] = slices[1:]
    last_slice = schedule[idx1[-1]:]
    dict_groups[last_slice[0]] = last_slice[1:]
    groups_list = list(dict_groups.keys())
    n = 4
    group_names = [groups_list[i * n:(i + 1) * n] for i in range((len(groups_list) + n - 1) // n)]
    my_keyboard = ReplyKeyboardMarkup(group_names, resize_keyboard=True)
    update.message.reply_text("Выберите группу:", reply_markup=my_keyboard)
    return "step_two"


def print_schedule(update, context):
    context.user_data["dialog"]["group"] = update.message.text
    book = openpyxl.open(new_elem_replace, read_only=True)
    sheet = book[context.user_data["dialog"]["sheet"]]
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
    groups = re.compile(r'(БД 12)|(БД 22)|(ИС 11)|(ИС 21)|(ИС 31)|(В 01)|(В 21)|(М 01)|(ПД 12)|(ПД 13)|(ПД 22)|(ПД 23)|(ПД 24)|(ПД 32)|(ПД 33)|(ПД 34)|(ПСО 11)|(ПСО 12)|(ПСО 21)|(ПСО 22)|(ПСО 31)|(ПСО 32)|(Т 11)|(Т 21)|(Т 31)|(УД 01)|(УД 11)|(УД 21)|(УД 31)|(Э 12)|(Э 22)')
    idx1 = [i for i, item in enumerate(schedule) if re.search(groups, item)]
    dict_groups = {}
    for i in range(len(idx1)-1):
        slices = schedule[idx1[i]:idx1[i+1]]
        dict_groups[slices[0]] = slices[1:]
    last_slice = schedule[idx1[-1]:]
    dict_groups[last_slice[0]] = last_slice[1:]
    selected_group = str(dict_groups[context.user_data["dialog"]["group"]]).replace(',','\n')
    my_keyboard = ReplyKeyboardMarkup([['Расписание'], ['Команды бота'], ['Звонки']], resize_keyboard=True)
    update.message.reply_text(selected_group, reply_markup=my_keyboard)
    return ConversationHandler.END


def main():
    mybot = Updater(settings.API_KEY, use_context=True)
    jq = mybot.job_queue
    jq.run_repeating(working_with_files, interval=3600, first=1)
    dp = mybot.dispatcher
    dialog = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.regex('^([Рр]асписание)$'), dialog_start)
        ],
        states={
            "step_one": [MessageHandler(Filters.regex('^((3[01]|[12][0-9]|0[1-9]).(1[0-2]|0[1-9]))$'), choose_sheet)],
            "step_two": [MessageHandler(Filters.regex('(([ЭМТВ].[0-4][0-4])|([ЭМТВ].[0-4])|([БУИП][ДС].[0-4][0-4]|[ИБПУ][СД].[0-4])|([П][С][О].[0-4][0-4])|([ВМ][0-4]|[У][Д][0-4]))'), print_schedule)]
        },
        fallbacks=[]
    )
    dp.add_handler(dialog)
    dp.add_handler(CommandHandler('subscribe', subscribe))
    dp.add_handler(CommandHandler('unsubscribe', unsubscribe))
    dp.add_handler(CommandHandler('show_rings', show_rings))
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(MessageHandler(Filters.regex('^([Зз]вонки)$'), show_rings))
    dp.add_handler(MessageHandler(Filters.regex('^([Кк]оманды бота)$'), bot_commands))
    logging.info("bot started")
    mybot.start_polling()
    mybot.idle()


if __name__ == "__main__":
    main()