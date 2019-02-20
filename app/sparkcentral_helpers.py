import hashlib
import hmac
import os
from binascii import unhexlify
from functools import wraps

from flask import request


def is_inbound_message():
    return request.json.get('type') == 'INBOUND_MESSAGE_RECEIVED'


def is_conversation_started():
    return request.json.get('type') == 'CONVERSATION_STARTED'


def get_message_text():
    return request.json.get('data', {}).get('message', {}).get('text')


def get_contact_profile():
    return request.json.get('data', {}).get('contactProfile') or {}


def get_contact_attributes():
    contact_attributes = request.json.get('data', {}).get('contactAttributes') or []
    return {x['attribute']: x['value'] for x in contact_attributes}


def get_conversation_id():
    return request.json.get('data', {}).get('conversationId')


def verify_signature(func):
    """
    Decorator that compares the X-Sparkcentral-Signature with the calculated signature based on a shared secret.
    Returns http status code 401 if it does not match.
    We expect the SPARKCENTRAL_VA_SECRET environment variable to contain the secret
    """

    @wraps(func)
    def decorated(*args, **kwargs):
        secret_key = unhexlify(os.environ['SPARKCENTRAL_VA_SECRET'])
        actual_signature = hmac.new(secret_key, request.data, hashlib.sha256).hexdigest()
        expected_signature = request.headers.get('X-Sparkcentral-Signature')

        if actual_signature != expected_signature:
            return f"X-Sparkcentral-Signature is invalid", 401

        return func(*args, **kwargs)

    return decorated
