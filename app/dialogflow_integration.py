from dialogflow import ContextsClient, SessionsClient, types
from google.protobuf import struct_pb2


class DialogflowClient:
    """
    A simplified client to talk to a dialogflow

    >>> bot = DialogflowClient('<dialogflow project id>')
    >>> response = bot.ask('1234', 'Hi!')
    >>> response.query_result.fulfillment_text
    'Good day! What can I do for you today?'
    """

    def __init__(self, project_id):
        """
        Initialize a Dialogflow ContextsClient/SessionsClient. See
        https://dialogflow.com/docs/reference/v2-auth-setup to setup credentials.

        :param project_id: The project id
        """

        self.context_client = ContextsClient()
        self.session_client = SessionsClient()
        self.project_id = project_id

    def create_context(self, conversation_id, context_name, attributes):
        """
        Adds attributes to Dialogflow context. The attributes can be used in Dialogflow responses by referencing eg.
        #contact_profile.primaryIdentifier

        :param conversation_id: The conversation id is used as session id in Dialogflow to differentiate different
                                conversations going on
        :param context_name: The name you want to use in Dialogflow to reference the attributes (eg contact_profile)
        :param attributes: A dictionary of key/values to be uploaded to Dialogflow
        """

        parent = self.context_client.session_path(self.project_id, conversation_id)
        parameters = struct_pb2.Struct()
        for key, value in attributes.items():
            parameters[key] = value

        self.context_client.create_context(
            parent,
            types.Context(
                name=f"projects/{self.project_id}/agent/sessions/{conversation_id}/contexts/{context_name}",
                lifespan_count=5,
                parameters=parameters,
            ),
        )

    def ask(self, conversation_id, question):
        """
        Pass a text message to Dialogflow and get back a DetectIntentResponse
        (https://cloud.google.com/dialogflow-enterprise/docs/reference/rpc/google.cloud.dialogflow.v2#detectintentresponse)

        :param conversation_id: The conversation id is used as session id in Dialogflow to differentiate different
                                conversations going on
        :param question: The text the contact sent
        :return: DetectIntentResponse containing the answer from the bot and other metadata.
        """

        session = self.session_client.session_path(self.project_id, conversation_id)
        query_input = types.QueryInput(
            text=types.TextInput(text=question, language_code="en-US")
        )
        return self.session_client.detect_intent(session, query_input)
