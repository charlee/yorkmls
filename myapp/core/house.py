# -*- coding: utf8 -*-

from .user import current_user_id
from .models import User, House
from pickle import dumps
import re
import time

def run_import_houses_task(url):

  from myapp.queue.tasks import import_houses_task

  import_houses_task.delay(current_user_id(), url)


def new_house(mls_id, user_id, address, pictures, price, data):
  house_id = House.new(id=mls_id, address=address, pictures=pictures, price=price, data=data, add_date=int(time.time()))
  user = User.ref(user_id)
  user.add_house(mls_id)

  return mls_id
  


def parse_house_info(table):

  address = table.xpath('tr/td/table[2]/tr/td[2]/table/tr[1]/td')[0].text_content().replace(u"\xa0", " ").strip()
  town = table.xpath('tr/td/table[2]/tr/td[2]/table/tr[2]/td')[0].text_content().replace(u"\xa0", " ").strip()
  price = table.xpath('tr/td/table[2]/tr/td[2]/table/tr[1]/td[2]')[0].text_content().replace(u"\xa0", " ").strip()
  mls_id = table.xpath('tr/td/table[2]/tr[3]/td/table/tr/td')[0].text_content().replace(u"\xa0", " ").strip()
  script_element = table.xpath('tr/td/table[2]/tr/td[1]/div/script')
  if script_element:
    script = script_element[0].text_content()
    images = re.search(r'new Array\(([^)]*)\)', script).group(1).split(',')
    images = map(lambda x:x.replace("'", ''), images)

  else:
    images = ['']

  image0 = table.xpath('tr/td/table[2]/tr/td[1]/div/img[1]/@src')[0]
  images[0] = str(image0)

  # fix address
  groups = re.search(r'(.* [A-Z][0-9][A-Z][0-9][A-Z][0-9]) .*', town)
  if groups:
    town = groups.group(1)

  address = "%s, %s" % (address, town)

  # fix price
  groups = re.search(r'(\$[0-9,]+).*', price)
  if groups:
    price = groups.group(1)

  return (mls_id, address, images, price)

