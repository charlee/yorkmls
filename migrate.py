#!/usr/bin/env python

import os
import sys
import time

from myapp import *
from myapp.queue import queue_daemon


keys = rds.keys("mls:house:*")

import pdb; pdb.set_trace()

for k in keys:

  data = rds.hget(k, 'data')
  mls_id = k.replace('mls:house:', '')
  rds.hmset("mls:house_data:%s.%s" % (mls_id, 0), dict(data=data, add_date=int(time.time())))
  rds.hmset(k, dict(data='', version_count=1))
