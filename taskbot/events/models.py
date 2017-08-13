# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from accounts.models import Account

class Event(models.Model):
    """
    """
    account     = models.ForeignKey(Account)
    unit        = models.CharField(max_length=500)
    rating      = models.CharField(max_length=500)
    choices     = models.CharField(max_length=500)
    truth       = models.CharField(max_length=500)

    time_created        = models.DateTimeField(auto_now_add=True)
    time_modified       = models.DateTimeField(auto_now=True)
