import logging
import os

from dotenv import load_dotenv
from google.cloud import dialogflow
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


LANGUAGE_CODE = 'ru'


def detect_intent_texts(project_id, session_id, texts, language_code):

    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    for text in texts:
        text_input = dialogflow.TextInput(text=text, language_code=language_code)

        query_input = dialogflow.QueryInput(text=text_input)

        response = session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        # print("Query text: {}".format(response.query_result.query_text))
        # print(
        #     "Detected intent: {} (confidence: {})\n".format(
        #         response.query_result.intent.display_name,
        #         response.query_result.intent_detection_confidence,
        #     )
        # )
        # print("Fulfillment text: {}\n".format(response.query_result.fulfillment_text))
    return response.query_result.fulfillment_text


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Здравствуйте')


def echo(update: Update, context: CallbackContext) -> None:
    text = [update.message.text]
    project_id = os.getenv("PROJECT_ID")
    update.message.reply_text(detect_intent_texts(project_id,
                                                  update.effective_user.id,
                                                  text,
                                                  LANGUAGE_CODE))

def main() -> None:
    load_dotenv()
    tg_token = os.getenv("TG_TOKEN")
    os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    updater = Updater(tg_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
