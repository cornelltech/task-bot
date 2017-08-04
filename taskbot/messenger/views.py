# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import traceback

import requests
from django.http import HttpResponse, JsonResponse
from django.views import View

from accounts.models import Account



def set_fb_getstarted_btn():
    # https://developers.facebook.com/docs/messenger-platform/messenger-profile/get-started-button
    req = requests.post(
        'https://graph.facebook.com/v2.6/me/messenger_profile',
        headers = { 'content-type':  'application/json' },
        params = { 'access_token': os.environ.get('FB_ACCESS_TOKEN', None) },
        data = json.dumps( {
            'payload': "Hey {{user_first_name}}! Let's play this game."
        } )
    )
    
    res = req.json()
    print "*"*50
    print res


def set_fb_greeting_msg():
    # https://developers.facebook.com/docs/messenger-platform/messenger-profile/greeting-text
    payload = {
        "greeting": [
            {
                "locale":"default",
                "text":"Hello!"
            }
        ] 
    }
    
    req = requests.post(
        'https://graph.facebook.com/v2.6/me/messenger_profile',
        headers = { 'content-type':  'application/json' },
        params = { 'access_token': os.environ.get('FB_ACCESS_TOKEN', None) },
        data = json.dumps( payload )
    )

    res = req.json()
    print "*"*50
    print res



def fetch_fb_user(psid):
    # https://graph.facebook.com/v2.6/<USER_ID>?access_token=PAGE_ACCESS_TOKEN
    req = requests.get(
        'https://graph.facebook.com/v2.6/{0}'.format(psid),
        headers = { 'content-type':  'application/json' },
        params = { 'access_token': os.environ.get('FB_ACCESS_TOKEN', None) },
    )

    res = req.json()

    if req.status_code == 200:
        fb_user_psid            = psid
        fb_user_first_name      = res.get('first_name', None)
        fb_user_last_name       = res.get('last_name', None)
        fb_user_profile_pic     = res.get('profile_pic', None)
        fb_user_locale          = res.get('locale', None)
        fb_user_gender          = res.get('gender', None)
        fb_user_timezone        = res.get('timezone', None)
        

        obj, created = Account.objects.get_or_create(
            fb_user_psid=fb_user_psid,
            fb_user_first_name=fb_user_first_name,
            fb_user_last_name=fb_user_last_name,
            fb_user_profile_pic=fb_user_profile_pic,
            fb_user_locale=fb_user_locale,
            fb_user_gender=fb_user_gender,
            fb_user_timezone=fb_user_timezone,
        )


def receive_message(event):
    sender_id       = event.get('sender').get('id')
    recipient_id    = event.get('recipient').get('id')
    time_of_message = event.get('timestamp')
    message         = event.get('message')

    print( 'Received MESSAGE for user {0} and page {1} at {2}'.format(sender_id, recipient_id, time_of_message) )

    message_id          = message.get('mid')
    message_text        = message.get('text')
    message_attachments = message.get('attachments')

    ########################################
    ########################################
    # fetch_fb_user(sender_id)

    # set_fb_getstarted_btn()

    # set_fb_greeting_msg()

    ########################################
    ########################################

    if message_text:
        if message_text == 'hi':
            send_generic_message(sender_id)
        elif message_text == 'btn':

            btns = [
                {
                    "type"      :"postback",
                    "title"     :"Start Chatting",
                    "payload"   :'BTN1'
                },
                {
                    "type"      :"postback",
                    "title"     :"other",
                    "payload"   :'BTN2'
                }
            ]

            send_btn_message(sender_id, message_text="hi there, click a btn", message_btns=btns)
        else:
            send_text_message(sender_id, message_text)
    elif message_attachments:
        send_text_message(sender_id, 'received attachments')

def receive_postback(event):
    sender_id       = event.get('sender').get('id')
    recipient_id    = event.get('recipient').get('id')
    time_of_message = event.get('timestamp')
    postback        = event.get('postback')

    print( 'Received POSTBACK for user {0} and page {1} at {2}'.format(sender_id, recipient_id, time_of_message) )

    postback_payload = postback.get('payload')
    postback_title   = postback.get('title')

    print( postback )


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


def send_btn_message(recipient_id, message_text=None, message_btns=[]):
    # https://developers.facebook.com/docs/messenger-platform/send-api-reference/button-template
    message_data = {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'attachment': {
                'type':'template',
                'payload': {
                    'template_type': 'button',
                    'text': message_text,
                    'buttons': message_btns
                }
            }
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
    
    res = req.json()

    if req.status_code == 200:
        recipient_id = res.get('message_id')
        message_id = res.get('message_id')
        print( 'Successfully sent generic message with id {0} to recipient {1}'.format(recipient_id, message_id) )

    else:
        print("Unable to send message")
        print( res )


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
                        elif msg.get('postback'):
                            receive_postback(msg)
                        else:
                            print( 'Webhook received unknown event: {0}'.format(event) )
            else:
                pass
        except Exception as e:
            print(e)
            print traceback.print_exc()
        

        response = JsonResponse({}, status=200)
        return response
