import pytest
from app import main
from binascii import unhexlify
import hmac
import os
import hashlib
import json


def test_accepts_correctly_signed_request(client, example_conversation_started):
    data, signature = calculate_secret(example_conversation_started)
    response = client.post('/webhook',
                           data=data,
                           headers={
                               "Content-Type": "application/json",
                               "X-Sparkcentral-Signature": signature
                           })

    assert 200 == response.status_code


def test_refuse_unsigned_requests(client, example_conversation_started):
    response = client.post('/webhook',
                           json=example_conversation_started,
                           headers={
                               "X-Sparkcentral-Signature": "Wrong"
                           })
    assert 401 == response.status_code


def test_returns_answer_for_inbound_message(client, example_inbound_message_received):
    data, signature = calculate_secret(example_inbound_message_received)
    response = client.post('/webhook',
                           data=data,
                           headers={
                               "Content-Type": "application/json",
                               "X-Sparkcentral-Signature": signature
                           })

    assert 200 == response.status_code
    assert json.loads(response.data)['sendMessage']['text'] in ["Hi! How are you doing?",
                                                                "Hello! How can I help you?",
                                                                "Good day! What can I do for you today?",
                                                                "Greetings! How can I assist?"]


@pytest.fixture
def client():
    main.app.config['TESTING'] = True
    client = main.app.test_client()
    return client


@pytest.fixture
def example_conversation_started():
    return {
        "timestamp": "2019-02-20T10:28:57.229144Z",
        "idempotencyKey": "36bce710-87d1-4b4c-9299-c873c34fac64",
        "version": 1,
        "type": "CONVERSATION_STARTED",
        "data": {
            "conversationId": "0-01e67a8c216-000-8c9ea98e",
            "contactProfile": {
                "id": "0-01e639d0a57-000-516b9710",
                "mediumContactProfileId": "2853168558034488",
                "primaryIdentifier": "Johan",
                "secondaryIdentifier": "",
                "pictureUrl": "https://sparkcentral-contact-profile-dev.s3.amazonaws.com/%3Fpsid%3D2853168558034488%26height%3D50%26width%3D50%26ext%3D1553182654%26hash%3DAeTadFdhVFqxmr28",
                "vip": False
            },
            "contactAttributes": [
                {"attribute": "smooch-rtm-page-title", "value": "In-Web Messaging Demo", "source": "MEDIUM"},
                {"attribute": "smooch-rtm-browser-language", "value": "en-GB", "source": "MEDIUM"},
            ],
            "medium": {"id": "smooch-rtm"},
            "channel": {"id": "0-01c6421333d-000-4a29abb0", "name": "Demo Channel"}
        }
    }


@pytest.fixture
def example_inbound_message_received():
    return {
        "timestamp": "2019-02-20T10:29:10.238188Z",
        "idempotencyKey": "5b784e97-34fa-11e9-bf33-f1b7c89708ca",
        "version": 1,
        "type": "INBOUND_MESSAGE_RECEIVED",
        "data": {
            "conversationId": "0-01e67a8c216-000-8c9ea98e",
            "message": {"text": "Hello"}
        }
    }


def calculate_secret(json_dict):
    data = json.dumps(json_dict).encode('utf-8')
    secret_key = unhexlify(os.environ['SPARKCENTRAL_VA_SECRET'])
    signature = hmac.new(secret_key, data, hashlib.sha256).hexdigest()
    return data, signature
