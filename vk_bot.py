import os
import random

import requests
import vk_api as vk
from dotenv import load_dotenv
from vk_api.longpoll import VkEventType, VkLongPoll

from google_dataflow_api import detect_intent_texts
from logs import set_logger

logger = set_logger()

def send_message(event, vk_api):
    project_id = os.getenv("PROJECT_ID")
    try:
        response = detect_intent_texts(project_id,
                                     event.user_id,
                                     event.text,
                                     'ru')

        if response.query_result.intent.is_fallback:
            answer = None
        else:
            answer = response.query_result.fulfillment_text

    except requests.exceptions.HTTPError as err:
        logger.error('Бот упал с ошибкой')
        logger.error(err, exc_info=True)


    if answer:
        try:
            vk_api.messages.send(
                user_id=event.user_id,
                message=answer,
                random_id=random.randint(1, 1000)
            )
        except vk_api.exceptions.VkApiError as err:
            logger.error('Бот упал с ошибкой')
            logger.error(err, exc_info=True)


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("VK_TOKEN")

    vk_session = vk.VkApi(token=token)
    logger.info('start dataflow vk bot')

    vk_api = vk_session.get_api()

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            send_message(event, vk_api)
