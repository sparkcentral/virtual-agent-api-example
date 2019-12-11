# Purpose

In this project we provide sample code for handling Virtual Agent webhook requests coming from Sparkcentral. You can learn
more about this api at [docs.sparkcentral.com/virtual-agent](https://docs.sparkcentral.com/virtual-agent/). 

In this sample code we show how to integrate with [Dialogflow](https://dialogflow.com). The code is deliberately kept simple 
and misses any logging, monitoring and persistence you might find in a production-ready adapter.   

# Configuration

You need to setup a couple environment variables in your .env file:

* `GOOGLE_APPLICATION_CREDENTIALS`: Should refer to the [Dialogflow auth file](https://dialogflow.com/docs/reference/v2-auth-setup)
* `DIALOGFLOW_PROJECT_ID`: Should refer to the Dialogflow project id.
* `SPARKCENTRAL_VA_SECRET`: The secret you received when creating a Virtual Agent in Sparkcentral
* `GIPHY_API_KEY`: An API key for Giphy. This allows you to test the attachment flow
* `SPARKCENTRAL_CLIENT_ID`: The OAuth2 client id. (If you don't have one, ask support@sparkcentral.com)
* `SPARKCENTRAL_CLIENT_SECRET`: The OAuth2 client secret.
* `SPARKCENTRAL_BASE_URL`: https://public-api.sparkcentral.com or https://public-api-eu.sparkcentral.com

# Build & Run

Given you defined these environment variables in a .env file, you can run:

```
docker build -t example_va .
docker run -it --env-file=.env -p 8080:80 example_va:latest
```

After that, you can use a tool like [ngrok](https://ngrok.com/) to forward a public internet address
to the locally running bot.

```
ngrok http 8080
# Forwarding                    https://abcdef.ngrok.io -> http://localhost:8080`
```
Now you can fill in the url https://abcdef.ngrok.io/webhook as a Virtual Agent webhook url. If you want to follow along what webhook calls are being sent, open http://127.0.0.1:4040/inspect/http

# Local development

Make sure you have python3 installed. 
Run `pip install -r requirements.txt`. It's recommended to use a python virtual env (eg `python3 -m venv venv` and run `. venv/bin/activate`). 

Run `FLASK_APP=app.main FLASK_ENV=development python -m flask run`. 
 

# Webhook

There is one main entrypoint being called by Sparkcentral: `/webhook` via a POST request. This is being handled in `app/main.py`. This
handles both a `CONVERSATION_STARTED` event and a `INBOUND_MESSAGE_RECEIVED` event. In the case of a `CONVERSATION_STARTED` event,
we can create a Dialogflow context, so the bot can use contact attributes in its responses and fulfillment calls. In the case
of an `INBOUND_MESSAGE_RECEIVED` event, we call `detect_intent` on the Dialogflow API. Dialogflow will answer us with a
`DetectIntentResponse`. This response contains the answer from the bot and other metadata (such as the detected intent, etc). In
our example we send the answer from the bot to the contact, and apply the detected intent as a topic.

In certain cases, you might want to send an answer using the REST API. You might want to send a message coming from one 
of your backend systems, or during a bot fulfillment. You can check out `app/rest_client.py` for this. You will need an
OAuth2 client-ID and client-secret. These are the same as for the CRM, Proactive API or Reporting API. If you don't have
OAuth2 credentials, you can contact support@sparkcentral.com.

* `app/main.py`. Main entrypoint defining the webhook endpoint
* `app/dialogflow_integration.py` Simple wrapper around Dialogflow client
* `app/sparkcentral_helpers.py` Utility methods for parsing json and verifying the `X-Sparkcentral-Signature`
* `app/rest_client.py` Sample REST client doing OAuth2 authentication to send messages, apply topics, resolve/handover a conversation. 