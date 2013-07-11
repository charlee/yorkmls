# -*- coding: utf8 -*-

from core.user import current_user_id
from core.models import User, House
from pickle import dumps

def run_import_houses_task(url):

  from queue.tasks import import_houses_task

  import_houses_task.delay(current_user_id(), url)


def new_house(mls_id, user_id, address, town, pictures, price, data):
  pictures = dumps(pictures)
  house_id = House.new(id=mls_id, address=address, town=town, pictures=pictures, price=price, data=data)
  user = User.ref(user_id)
  user.add_house(mls_id)

  return mls_id
  
