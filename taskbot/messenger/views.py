# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os

from django.http import HttpResponse, JsonResponse
from django.views import View


# Create your views here.
class FBWebhookResponseView(View):
    def get(self, request, *args, **kwargs):
        TOKEN = os.environ.get('FB_CHALLENGE', None)

        requestUrlParams = request.GET
        if requestUrlParams.get('hub.mode', None) == 'subscribe' and requestUrlParams.get('hub.verify_token', None) == TOKEN:
            challenge = requestUrlParams.get('hub.challenge')
            return HttpResponse( challenge, status=200 )
        else:
            return HttpResponse( status=403 )

    def post(self, request, *args, **kwargs):

        requestBody = json.loads(request.body)

        print requestBody

        # if (req.query['hub.mode'] === 'subscribe' &&
        #     req.query['hub.verify_token'] === <VERIFY_TOKEN>) {
        #     console.log("Validating webhook");
        #     res.status(200).send(req.query['hub.challenge']);
        # } else {
        #     console.error("Failed validation. Make sure the validation tokens match.");
        #     res.sendStatus(403);          
        # }  

        response = JsonResponse({}, status=200)
        return response
