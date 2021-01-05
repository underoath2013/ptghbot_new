import logging
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import openpyxl
import settings

logging.basicConfig(filename="bot.log", level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def greet_user(update, context):
    print("Вызван /start")
    book = openpyxl.open('ismen_nov.xlsx', read_only=True)
    my_keyboard = ReplyKeyboardMarkup([book.sheetnames], resize_keyboard=True)
    update.message.reply_text("Изменения к расписанию занятий Корпус 1 (ул. Мурманская, д. 30) \n выберите дату:", reply_markup=my_keyboard)

def choosing_sheets(update, context, sheet_name):
    book = openpyxl.open('ismen_nov.xlsx', read_only=True)
    sheet = book[sheet_name]
    for row in range(1, sheet.max_row):
        a_column = sheet[row][0].value
        if a_column is None:
            a_column = ''
        c_column = sheet[row][2].value
        if c_column is None:
            c_column = ''
        b_column = sheet[row][1].value
        if b_column is None:
            continue
        else:
            b_column_split = ' '.join(b_column.split())
            result_abc = str(a_column) + str(b_column_split) + ' ' + str(c_column)
            print(result_abc)
    for row in range(1, sheet.max_row):
        e_column = sheet[row][4].value
        if e_column is None:
            e_column = ''
        g_column = sheet[row][6].value
        if g_column is None:
            g_column = ''
        f_column = sheet[row][5].value
        if f_column is None:
            continue
        else:
            f_column_split = ' '.join(f_column.split())
            result_efg = str(e_column) + str(f_column_split) + ' ' + str(g_column)
            print(result_efg)
    update.message.reply_text(choosing_sheets)


def main():
    mybot = Updater(settings.API_KEY, use_context=True)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("show", choosing_sheets))
        
    logging.info("bot started")
    mybot.start_polling()
    mybot.idle()


if __name__ == "__main__":
    main()
