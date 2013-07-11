# -*- coding: utf8 -*-

from .user import current_user_id
from .models import User, House
from pickle import dumps
import time

def run_import_houses_task(url):

  from myapp.queue.tasks import import_houses_task

  import_houses_task.delay(current_user_id(), url)


def new_house(mls_id, user_id, address, pictures, price, data):
  pictures = dumps(pictures)
  house_id = House.new(id=mls_id, address=address, pictures=pictures, price=price, data=data, add_date=int(time.time()))
  user = User.ref(user_id)
  user.add_house(mls_id)

  return mls_id
  
