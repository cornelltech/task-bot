# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os

import requests
from django.http import HttpResponse, JsonResponse
from django.views import View


def receive_message(event):
    sender_id       = event.get('sender').get('id')
    recipient_id    = event.get('recipient').get('id')
    time_of_message = event.get('timestamp')
    message         = event.get('message')

    print( 'Received message for user {0} and page {1} at {2} with message:'.format(sender_id, recipient_id, time_of_message) )

    message_id          = message.get('mid')
    message_text        = message.get('text')
    message_attachments = message.get('attachments')

    if message_text:
        if message_text == 'hi':
            send_generic_message(sender_id)
        else:
            send_text_message(sender_id, message_text)
    elif message_attachments:
        send_text_message(sender_id, 'received attachments')


def send_generic_message(recipient_id):
    message_data = {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': 'Hello you special you'
        }
    }

    call_send_api(message_data)


def send_text_message(recipient_id, message_text):
    message_data = {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': message_text
        }
    }

    call_send_api(message_data)


def call_send_api(message_data): 

    req = requests.post(
        'https://graph.facebook.com/v2.6/me/messages',
        headers = { 'content-type':  'application/json' },
        params = { 'access_token': os.environ.get('FB_ACCESS_TOKEN', None) },
        data = json.dumps( message_data )
    )
    
    res = json.loads( req.json() )

    if req.status_code == 200:
        recipient_id = res.get('message_id')
        message_id = res.get('message_id')
        print( 'Successfully sent generic message with id {0} to recipient {1}'.format(recipient_id, message_id) )

    else:
        print("Unable to send message")
        print( res.json() )


# Create your views here.
class FBWebhookResponseView(View):
    def get(self, request, *args, **kwargs):
        TOKEN = os.environ.get('FB_CHALLENGE', None)

        request_url_params = request.GET
        if request_url_params.get('hub.mode', None) == 'subscribe' and request_url_params.get('hub.verify_token', None) == TOKEN:
            challenge = request_url_params.get('hub.challenge')
            return HttpResponse( challenge, status=200 )
        else:
            return HttpResponse( status=403 )

    def post(self, request, *args, **kwargs):

        request_body = json.loads(request.body)

        try:
            if request_body.get('object') == 'page':
            
                #  Make sure this is a page subscription
                entry = request_body.get('entry')
                
                # Iterate over each entry - there may be multiple if batched
                for obj in entry:
                    page_id = obj.get('id')
                    time_of_event = obj.get('time')

                    # Iterate over each messaging event
                    messaging = obj.get('messaging')
                    for msg in messaging:
                        if msg.get('message'):
                            receive_message(msg)
                        else:
                            print( 'Webhook received unknown event: {0}'.format(event) )
            else:
                pass
        except Exception as e:
            print(e)
        

        response = JsonResponse({}, status=200)
        return response
