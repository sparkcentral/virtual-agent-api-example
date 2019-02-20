import logging
import os
from flask import Flask, jsonify
from app.dialogflow_integration import DialogflowClient
from app.sparkcentral_helpers import verify_signature, is_conversation_started, get_conversation_id, \
    get_contact_profile, get_contact_attributes, is_inbound_message, get_message_text
from os.path import basename
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
@verify_signature
def webhook():
    bot = DialogflowClient(os.environ['DIALOGFLOW_PROJECT_ID'])
    if is_conversation_started():
        # In a conversation_started event we get information on the contact, which we store
        # in a Dialogflow context. That way the bot can use the information in its answers/fulfillments.
        # You could for example use "Hello #contact_profile.primaryIdentifier" in Dialogflow.

        bot.create_context(get_conversation_id(), 'contact_profile', get_contact_profile())
        bot.create_context(get_conversation_id(), 'contact_attributes', get_contact_attributes())
        return jsonify()

    elif is_inbound_message():
        response = bot.ask(get_conversation_id(), get_message_text())

        return jsonify(
            sendMessage={'text': response.query_result.fulfillment_text},
            applyTopics=[response.query_result.intent.display_name],
            complete=__get_complete_for(response))
    else:
        # In the future new events might be introduced. Avoid returning error if you encounter a new event. Instead just
        # return an empty json with 200 OK
        return jsonify()


def __get_complete_for(response):
    """
    Return a HANDOVER (put conversation in new queue for human agent) or RESOLVED (put conversation in resolved queue)
    for certain responses. There are multiple strategies possible. You could keep a hard-coded list of intents for which
    to resolve/handover, use the end-conversation flag in diagnostic-info in the response, add some specific attribute
    or output context.

    :param response: The DetectIntentResponse response from the bot.
    :return: HANDOVER (hand over to human), RESOLVED (put in resolved) or None (keep conversation)
    """

    output_context_names = [basename(context.name) for context in response.query_result.output_contexts]

    if response.query_result.action == 'input.unknown':
        return 'HANDOVER'
    elif 'handover-human' in output_context_names:
        return 'HANDOVER'
    elif 'handover-resolved' in output_context_names:
        return 'RESOLVED'
    else:
        return None


gunicorn_logger = logging.getLogger('gunicorn.error')
if gunicorn_logger.handlers:
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
