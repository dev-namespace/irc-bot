#!/usr/bin/env python
import pytz

def get_cest_datetime():
    from datetime import datetime
    return datetime.now(pytz.timezone('Europe/Berlin'))
