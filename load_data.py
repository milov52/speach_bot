import argparse
import json
import os

from dotenv import load_dotenv
from google.cloud import dialogflow


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    intents_client = dialogflow.IntentsClient()

    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)

        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name, training_phrases=training_phrases, messages=[message]
    )

    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )

    print("Intent created: {}".format(response))


def main():
    parser = argparse.ArgumentParser(
        description='Загрузка вопросов и ответов из файла'
    )
    parser.add_argument('source', help='Путь к файлу с вопросами')
    args = parser.parse_args()

    load_dotenv()
    project_id = os.getenv('PROJECT_ID')

    with open(args.source, 'r') as phrases_file:
        phrases_json = phrases_file.read()
    phrases = json.loads(phrases_json)

    for intent, intent_value in phrases.items():
        create_intent(project_id, intent, intent_value['questions'], [intent_value['answer']])

if __name__ == '__main__':
    main()