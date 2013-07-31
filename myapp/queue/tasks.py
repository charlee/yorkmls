from . import queue_task, get_tmp_param

import urllib2

from lxml import etree
from lxml.html import fromstring
from datetime import datetime
from myapp.core.models import User
from myapp.core.house import new_house, parse_house_info


ADDR_ABBR = {
  'ave': 'Avenue',
  'cres': 'Crescent',
  'blvd': 'Boulevard',
}


@queue_task
def import_houses_task(user_id, url):

  html_string = urllib2.urlopen(url).read()
  user_ref = User.ref(user_id)

  if html_string:

    root = fromstring(html_string)

    body = [ e for e in root.getchildren() if e.tag.lower() == 'body' ]
    if len(body) > 0:
      body = body[0]

      tables = [ e for e in body.getchildren() if e.tag.lower() == 'table' ]

      for table in tables:

        mls_id, address, images, price = parse_house_info(table)

        mls_id = new_house(mls_id, address, images, price, etree.tostring(table))

        # if updated, add it to user's database
        if mls_id != 0:
          user_ref.restore_house(mls_id)
          user_ref.add_house(mls_id)

