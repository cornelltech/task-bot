# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import traceback

import requests
from django.http import HttpResponse, JsonResponse
from django.views import View

from accounts.models import Account
from units.units import pick_listing


def set_fb_getstarted_btn():
    # https://developers.facebook.com/docs/messenger-platform/messenger-profile/get-started-button
    req = requests.post(
        'https://graph.facebook.com/v2.6/me/messenger_profile',
        headers = { 'content-type':  'application/json' },
        params = { 'access_token': os.environ.get('FB_ACCESS_TOKEN', None) },
        data = json.dumps( {
            'get_started': {
                'payload': "START"
            }
        } )
    )
    
    res = req.json()


def set_fb_menu():
    # https://developers.facebook.com/docs/messenger-platform/messenger-profile/persistent-menu#testing

    payload = {
        'persistent_menu': [
            {
                'locale': 'default',
                'composer_input_disabled': True,
                'call_to_actions': [
                    {
                        'type': 'postback',
                        'title': 'Guess the price!',
                        'payload': 'PLAY'
                    },
                    {
                        'type': 'postback',
                        'title': 'My Score',
                        'payload': 'SCORE'
                    },
                    {
                        'type': 'postback',
                        'title': 'About',
                        'payload': 'ABOUT'
                    },
                ]
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


def set_fb_greeting_msg():
    # https://developers.facebook.com/docs/messenger-platform/messenger-profile/greeting-text
    payload = {
        "greeting": [
            {
                "locale":"default",
                "text":"Hey there! Let's find out how street savy you are. We'll show you a few apartments in NYC and all you have to do is guess what their price is!"
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
    message_quickreply  = message.get('quick_reply', None)
    message_attachments = message.get('attachments')

    if message_quickreply is not None:
        print("*"*50)
        print(event)


def receive_postback(event):
    sender_id       = event.get('sender').get('id')
    recipient_id    = event.get('recipient').get('id')
    time_of_message = event.get('timestamp')
    postback        = event.get('postback')

    print( 'Received POSTBACK for user {0} and page {1} at {2}'.format(sender_id, recipient_id, time_of_message) )

    postback_payload = postback.get('payload')
    postback_title   = postback.get('title')

    """
    Options are:
        START
        PLAY
        SCORE
        ABOUT
    """

    if postback_payload == 'START':
        fetch_fb_user(sender_id)

        send_text_message(sender_id, "Hey there! Thanks for playing, let's start with this apartment!")

    elif postback_payload == 'PLAY':
        
        unit = pick_listing(sender_id)
        
        if unit is None:
            send_text_message(sender_id, 'Sorry, looks like we have no more apartments to show you, come play later :)')
            return
        
        quick_buttons = [
                {
                    "content_type"  :"text",
                    "title"         :"Yes",
                    "payload"       :"BROWSE",
                },
                {
                    "content_type"  :"text",
                    "title"         :"No",
                    "payload"       :"BROWSE",
                },
            ]
        send_quick_replay_message(sender_id, 'How much do you think this is?', quick_buttons)


    elif postback_payload == 'SCORE':
        send_text_message(sender_id, 'Your score is ...')

    elif postback_payload == 'ABOUT':
        send_text_message(sender_id, 'This is a project that does ...')


def send_generic_message(recipient_id):
    message_data = {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': 'Sorry, I didn\'t get that :/' 
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


def send_generic_template_message(recipient_id, elements=[]):
    # https://developers.facebook.com/docs/messenger-platform/send-api-reference/generic-template
    message_data = {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'attachment': {
                'type':'template',
                'payload': {
                    'template_type': 'generic',
                    'elements': elements
                }
            }
        }
    }

    call_send_api(message_data)


def send_quick_replay_message(recipient_id, message_text=None, message_btns=[]):
    # https://developers.facebook.com/docs/messenger-platform/send-api-reference/quick-replies
    message_data = {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': message_text,
            'quick_replies': message_btns
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

    def put(self, request, *args, **kwargs):
        print "Configuring Messenger"

        try:
            
            set_fb_greeting_msg()
            set_fb_getstarted_btn()
            set_fb_menu()
            
            return HttpResponse( status=200 )

        except Exception as e:
            
            print(e)
            print(traceback.print_exc())

            return HttpResponse( status=400 )
        

        


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
            print(traceback.print_exc())
        

        response = JsonResponse({}, status=200)
        return response
