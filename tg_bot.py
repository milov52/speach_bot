import logging
import os

import telegram
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

from google_dataflow_api import detect_intent_texts
from handlers import TelegramLogsHandler

logger = logging.getLogger('Logger')



def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Здравствуйте')


def send_message(update: Update, context: CallbackContext) -> None:
    project_id = os.getenv("PROJECT_ID")
    response = detect_intent_texts(project_id,
                                   update.effective_user.id,
                                   update.message.text,
                                   'ru')
    update.message.reply_text(response.query_result.fulfillment_text)


def main() -> None:
    load_dotenv()
    tg_token = os.getenv("TG_TOKEN")
    tg_logger_token = os.getenv("TG_LOGGER_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")

    bot_logger = telegram.Bot(token=tg_logger_token)

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )

    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(bot_logger, chat_id))

    logger.info('start dataflow tg bot')
    try:
        updater = Updater(tg_token)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, send_message))

        updater.start_polling()
        updater.idle()
    except Exception as err:
        logger.error('Бот упал с ошибкой')
        logger.error(err, exc_info=True)


if __name__ == '__main__':
    main()
