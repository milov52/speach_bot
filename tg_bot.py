import os

import google.api_core.exceptions
import requests
from dotenv import load_dotenv
from google.cloud import dialogflow
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

from logs import set_logger

logger = set_logger()


def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    try:
        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
    except google.api_core.exceptions.GoogleAPIError as err:
        logger.error('Бот упал с ошибкой')
        logger.error(err, exc_info=True)

    return response.query_result.fulfillment_text


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Здравствуйте')


def send_message(update: Update, context: CallbackContext) -> None:
    project_id = os.getenv("PROJECT_ID")
    try:
        update.message.reply_text(detect_intent_texts(project_id,
                                                      update.effective_user.id,
                                                      update.message.text,
                                                      'ru'))
    except telegram.error.TelegramError as err:
        logger.error('Бот упал с ошибкой')
        logger.error(err, exc_info=True)


def main() -> None:
    load_dotenv()
    tg_token = os.getenv("TG_TOKEN")

    os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    logger.info('start dataflow tg bot')
    try:
        updater = Updater(tg_token)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, send_message))

        updater.start_polling()
        updater.idle()
    except telegram.error.TelegramError as err:
        logger.error('Бот упал с ошибкой')
        logger.error(err, exc_info=True)

if __name__ == '__main__':
    main()
