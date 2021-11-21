try:
   import unzip_requirements
except ImportError:
   pass

import json
import os
import boto3
import logging

from boto3.dynamodb.conditions import Key, Attr
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
from twilio.twiml.messaging_response import Body, Message, Redirect, MessagingResponse


LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

if os.environ.get('IS_OFFLINE') != True:
    patch_all()

lambda_client = boto3.client('lambda')


def _get_event_body(event):
    try:
        return json.loads(event.get("body", ""))
    except ValueError:
        LOG.error("event body could not be JSON decoded.")
        return {}


def _get_event_header(event):
    try:
        return json.loads(event.get("headers", ""))
    except ValueError:
        LOG.error("event headers could not be JSON decoded.")
        return {}


def twilio_webhook_handler(event, context):

    headers = _get_event_header(event)
    if headers.get("X-Twilio-Signature") != os.environ.get("TWILIO_ACCOUNT_KEY"):
        return {
            "statusCode": 400,
            "body": "Webhook verification failed."
        }

    body = _get_event_body(event)

    lambda_client.invoke(
        FunctionName='lambda-function-name',  # TODO: Replace with real function name
        InvocationType='Event',
        Payload=json.dumps(body)
    )

    response = MessagingResponse()
    message = Message()
    message.body('Hello World!')    # TODO: Replace with real response message body
    response.append(message)
    response.redirect('https://demo.twilio.com/welcome/sms/')   # TODO: Replace with real redirect url
    return response
