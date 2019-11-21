import boto3
import json
import logging
import time

# Django specific settings
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Ensure settings are read
application = get_wsgi_application()

# Your application specific imports
from data.models import *

logger = logging.getLogger("serverless")
logger.setLevel(logging.DEBUG)



def connection_manager(event, context):
    """
    Handles connecting and disconnecting for the Websocket.
    """
    logger.info(" connection_manager.")
    connection_id = event["requestContext"].get("connectionId")
    
    if event["requestContext"]["eventType"] == "CONNECT":
        logger.info("Connect requested")

        Connection(connection_id=connection_id).save()
        return _get_response(200, "Connect successful.")
    elif event["requestContext"]["eventType"] == "DISCONNECT":
        logger.info("Disconnect requested")

        Connection.objects.filter(connection_id=connection_id).delete()
        return _get_response(200, "Disconnect successful.")
    else:
        logger.error("Connection manager received unrecognized eventType.")
        return _get_response(500, "Unrecognized eventType.")


def send_message(event, context):
    """
    When a message is sent on the socket, forward it to all connections.
    """
    logger.info("Message sent on WebSocket.")

    # Ensure all required fields were provided
    body = _get_body(event)
    for attribute in ["username", "content"]:
        if attribute not in body:
            logger.debug("Failed: '{}' not in message dict."\
                    .format(attribute))
            return _get_response(400, "'{}' not in message dict"\
                    .format(attribute))
                
    # Add the new message to the database
    Message(
        username=body['username'],
        content=body['content'],
        timestamp=body['timestamp'],
        user_profile_img='imag.jpg',
        room_id=1,
    ).save()

    # # Get all current connections
    connections = Connection.objects.all()

    # # Send the message data to all connections
    message = {
        "username": body['username'], 
        "content": body['content'],
        "timestamp":body['timestamp']
    }
    logger.debug("Broadcasting message: {}".format(message))
    data = {"messages": [message]}
    for connection in connections:
        _send_to_connection(
            # connection['connection_id'], data, event
            connection.connection_id, data, event
        )

    return _get_response(200, "Message sent to all connections.")


def get_recent_messages(event, context):
    """
    Return the 10 most recent chat messages.
    """
    logger.info("Retrieving most recent messages.")
    connection_id = event["requestContext"].get("connectionId")

    # Get the 10 most recent chat messages
    recent_messages = Message.objects.all().order_by('-pk')[:10]

    # Extract the relevant data and order chronologically
    messages = [
        {
            "username": m.username, 
            "content": m.content,
            "timestamp":m.timestamp
        } for m in recent_messages
    ]
   
    messages.reverse()

    # # Send them to the client who asked for it
    data = {"messages": messages}
    _send_to_connection(connection_id, data, event)

    return _get_response(200, "Sent recent messages.")


def default_message(event, context):
    """
    Send back error when unrecognized WebSocket action is received.
    """
    logger.info("Unrecognized WebSocket action received.")
    return _get_response(400, "Unrecognized WebSocket action.")


def ping(event, context):
    """
    Sanity check endpoint that echoes back 'PONG' to the sender.
    """
    logger.info("Ping requested.")
    return _get_response(200, "PONG!")






#Helpers
def _get_response(status_code, body):
    if not isinstance(body, str):
        body = json.dumps(body)
    return {"statusCode": status_code, "body": body}

def _get_body(event):
    try:
        return json.loads(event.get("body", ""))
    except:
        logger.debug("event body could not be JSON decoded.")
        return {}

def _send_to_connection(connection_id, data, event):
    gatewayapi = boto3.client("apigatewaymanagementapi",
            endpoint_url = "https://" + event["requestContext"]["domainName"] +
                    "/" + event["requestContext"]["stage"])
    return gatewayapi.post_to_connection(ConnectionId=connection_id,
            Data=json.dumps(data).encode('utf-8'))