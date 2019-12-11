from flask import request
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from app.sparkcentral_helpers import get_random_giphy


class RestClient:
    """
    Allows sending messages/adding topics/completing a conversation via the REST api. This can be usefull if your
    bot-platform works in an asynchronous fashion, or if you want to do something to the conversation in a
    bot-fulfillment.

    >>> rest_client = RestClient(client_id='<oauth client id>',
    ...                          client_secret='<oauth client id>',
    ...                          base_url='https://public-api.sparkcentral.com') # Or public-api-eu
    >>> rest_client.send('0-01d90bc1b13-000-9a9ca0d8', text="Let me get you a human agent", complete="HANDOVER")
    <Response [200]>
    """

    def __init__(self, client_id, client_secret, base_url):
        """
        Creates a rest client to use the Virtual Agent REST api. You need OAuth2 credentials. These are the same as for
        the CRM/Proactive messaging/Reporting APIs. You can also contact support@sparkcentral.com if you didn't receive
        these yet.

        :param client_id: OAuth2 Client ID
        :param client_secret: OAuth2 Client Secret
        :param base_url: 'https://public-api.sparkcentral.com' (US cluster) or 'https://public-api-eu.sparkcentral.com'
                         (EU cluster)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        client = BackendApplicationClient(client_id=client_id)
        self.request_client = OAuth2Session(client=client)

    def fetch_oauth_token(self):
        self.request_client.fetch_token(
            token_url=f"{self.base_url}/virtual-agent/oauth2/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope="client-read",
        )

    def upload_attachment(self, conversation_id, binary_data, filename, content_type):
        """
        Uploads an attachment that can be sent as part of a message. 

        :param conversation_id: The id of the conversation. The attachment can only be sent in the context of this conversation
        :param binary_data: The actual bytes to send. 
        :param filename: The filename of the attachment. This is used when sending a message, and will be visible to the contact when they download
        :param content_type: The mime type of the attachment. Needs to be correct to make sure contacts sees it inline in their chat window
        :returns Response from server. Status code 200 if accepted. 404 if conversation not assigned to Virtual Agent
        """
        self.fetch_oauth_token()
        # Note, Content-Length is also required, but in this case requests library adds it automatically
        return self.request_client.put(
            f"{self.base_url}/virtual-agent/conversations/{conversation_id}/attachments/{filename}",
            data=binary_data,
            headers={"Content-Type": content_type},
        )

    def send(
        self, conversation_id, text=None, attachment=None, topics=None, complete=None
    ):
        """
        Authenticates using oauth2 and allows sending a message, apply a topic, resolve or handover a conversation.
        Note, if the conversation is not assigned to your virtual agent, you will receive a 404.

        :param conversation_id: The id of the conversation
        :param text: Text of the message you want to send. Can be None if you don't want to send a message
        :param attachment: Filename of the attachment you want to send. Needs to be uploaded first
        :param topics: List of topics you want to apply. Needs to match exactly with the topic name. If it doesn't
                       match, that topic will be ignored. Can be None if you don't want to apply topics.
        :param complete: "RESOLVED" if you want to resolve the conversation or "HANDOVER" if you want to pass it to
                         a human agent. Can be None if you don't want to do either.
        :returns Response from server. Status code 200 if accepted. 404 if conversation not assigned to Virtual Agent
        """
        self.fetch_oauth_token()
        if text or attachment:
            message = {"text": text, "attachment": attachment}
        else:
            message = None

        return self.request_client.post(
            f"{self.base_url}/virtual-agent/conversations/{conversation_id}",
            json={"sendMessage": message, "applyTopics": topics, "complete": complete},
        )
