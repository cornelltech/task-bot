# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Account

# Register your models here.
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'fb_user_psid', 'fb_user_first_name', 'fb_user_last_name', 'fb_user_profile_pic', 'fb_user_locale', 'fb_user_gender', 'fb_user_timezone', 'time_created', 'time_modified',)
    list_display_links = ('fb_user_psid',)
admin.site.register(Account, AccountAdmin)