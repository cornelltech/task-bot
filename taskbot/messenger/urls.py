from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from .views import FBWebhookResponseView

urlpatterns = [
    url(r'^callback', csrf_exempt( FBWebhookResponseView.as_view() ), name='callback'),
]