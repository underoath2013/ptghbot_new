import logging
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
import openpyxl
import settings
import re
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import urllib.request
import config

logging.basicConfig(filename="bot.log", level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def download_file_greet_user(update, context):
    print("Вызван /start")
    url = Request(config.DATASET_URL)
    html_page = urlopen(url)
    soup = BeautifulSoup(html_page, "html.parser")
    link = []
    for item in soup.findAll('a'):
        link.append(item.get('href'))
    for index, elem in enumerate(link):
        if (elem.find('ismen_nov')) != -1:
            print(elem)
            break
    file_xls = urllib.request.urlopen(elem).read()
    f = open(config.ISMEN_FILE_NAME, "wb")
    f.write(file_xls)
    f.close()
    my_keyboard = ReplyKeyboardMarkup([['Расписание']], resize_keyboard=True)
    update.message.reply_text("Привет, чтобы узнать расписание нажми кнопку", reply_markup=my_keyboard)


def dialog_start(update, context):
    book = openpyxl.open(config.ISMEN_FILE_NAME, read_only=True)
    my_keyboard = ReplyKeyboardMarkup([book.sheetnames], resize_keyboard=True)
    update.message.reply_text("Изменения к расписанию занятий Корпус 1 (ул. Мурманская, д. 30) \n выберите дату:", reply_markup=my_keyboard)
    return "step_one"

def choose_sheet(update, context):
    book = openpyxl.open(config.ISMEN_FILE_NAME, read_only=True)
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
    groups = re.compile(r'([ЭМТВ]\s[0-4][0-4])|([ЭМТВ]\s[0-4])|([БУИП][ДС]\s[0-4][0-4]|[ИБПУ][СД]\s[0-4])|([П][С][О]\s[0-4][0-4])|([ВМ][0-4]|[У][Д][0-4])')
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
    book = openpyxl.open(config.ISMEN_FILE_NAME, read_only=True)
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
    groups = re.compile(r'([ЭМТВ]\s[0-4][0-4])|([ЭМТВ]\s[0-4])|([БУИП][ДС]\s[0-4][0-4]|[ИБПУ][СД]\s[0-4])|([П][С][О]\s[0-4][0-4])|([ВМ][0-4]|[У][Д][0-4])')
    idx1 = [i for i, item in enumerate(schedule) if re.search(groups, item)]
    dict_groups = {}
    for i in range(len(idx1)-1):
        slices = schedule[idx1[i]:idx1[i+1]]
        dict_groups[slices[0]] = slices[1:]
    last_slice = schedule[idx1[-1]:]
    dict_groups[last_slice[0]] = last_slice[1:]
    selected_group = str(dict_groups[context.user_data["dialog"]["group"]]).replace(',','\n')
    my_keyboard = ReplyKeyboardMarkup([['Расписание']], resize_keyboard=True)
    update.message.reply_text(selected_group, reply_markup=my_keyboard)
    return ConversationHandler.END


def main():
    mybot = Updater(settings.API_KEY, use_context=True)

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

    dp.add_handler(CommandHandler("start", download_file_greet_user))
    logging.info("bot started")
    mybot.start_polling()
    mybot.idle()


if __name__ == "__main__":
    main()


