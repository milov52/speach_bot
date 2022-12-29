import os
import random

import google.api_core.exceptions
import requests
import vk_api as vk
from dotenv import load_dotenv
from google.cloud import dialogflow
from vk_api.longpoll import VkEventType, VkLongPoll
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

    if response.query_result.intent.is_fallback:
        return None
    else:
        return response.query_result.fulfillment_text


def send_message(event, vk_api):
    project_id = os.getenv("PROJECT_ID")
    try:
        answer = detect_intent_texts(project_id,
                                     event.user_id,
                                     event.text,
                                     'ru')
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
    vk_api = vk_session.get_api()

    logger.info('start dataflow vk bot')
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            send_message(event, vk_api)
