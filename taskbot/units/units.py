# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import traceback
import random 

from events.models import Event

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNITS_DATA  = os.path.join(BASE_DIR, "units/data/2017-07-29-sales-units.json")


def read_file(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        return data

def pick_listing(account_id):
    try:
        data = read_file(UNITS_DATA)
        
        unit_permalink = random.choice( data.keys() )

        if Event.objects.filter(account__fb_user_psid=account_id, unit=unit_permalink).count() > 0:
            return None

        return data[unit_permalink]

    except Exception as e:
        print(e)
        print(traceback.print_exc())
        return None
    

def generate_choices(account_id, listing):
    pass

def make_choice(account_id, listing, rating):
    pass