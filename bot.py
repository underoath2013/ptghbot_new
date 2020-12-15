import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import settings

logging.basicConfig(filename="bot.log", level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def greet_user(update, context):
    print("Вызван /start")
    update.message.reply_text("Здравствуйте, я бот ПТГХ!")



def main():
    mybot = Updater(settings.API_KEY, use_context=True)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    

    logging.info("bot started")
    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()