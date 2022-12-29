from google.cloud import dialogflow
import google.api_core.exceptions
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

    return response