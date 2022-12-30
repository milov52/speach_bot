import logging
import os
import random

import telegram
import vk_api as vk
from dotenv import load_dotenv
from vk_api.longpoll import VkEventType, VkLongPoll

from google_dataflow_api import detect_intent_texts
from handlers import TelegramLogsHandler

logger = logging.getLogger('Logger')



def send_message(event, vk_api):
    project_id = os.getenv("PROJECT_ID")
    response = detect_intent_texts(project_id,
                                   event.user_id,
                                   event.text,
                                   'ru')

    if not response.query_result.intent.is_fallback:
        vk_api.messages.send(
            user_id=event.user_id,
            message= response.query_result.fulfillment_text,
            random_id=random.randint(1, 1000)
        )

if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("VK_TOKEN")

    tg_logger_token = os.getenv("TG_LOGGER_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")

    bot_logger = telegram.Bot(token=tg_logger_token)

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )

    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(bot_logger, chat_id))

    try:
        vk_session = vk.VkApi(token=token)
        logger.info('start dataflow vk bot')

        vk_api = vk_session.get_api()

        longpoll = VkLongPoll(vk_session)
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                send_message(event, vk_api)
    except Exception as err:
        logger.error('Бот упал с ошибкой')
        logger.error(err, exc_info=True)
