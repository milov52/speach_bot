import logging
import os

import telegram
from dotenv import load_dotenv


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def set_logger():
    load_dotenv()
    tg_logger_token = os.getenv("TG_LOGGER_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )

    logger = logging.getLogger('Logger')

    bot_logger = telegram.Bot(token=tg_logger_token)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(TelegramLogsHandler(bot_logger, chat_id))

    return logger
