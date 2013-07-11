from . import queue_task, get_tmp_param

import urllib2

import lxml
from datetime import datetime
from core.models import User, Pin, Link
from core.pin import new_pin


@queue_task
def import_houses_task(user_id, url):

  html_string = urllib2.urlopen(url).read()

  if html_string:

  root = lxml.html.fromstring(html_string)
  for t in root.iterlinks():
    a = t[0]

    icon = a.get('icon', '')
    url = a.get('href')
    add_date = a.get('add_date')

    # tags property from delicious
    tags = filter(None, a.get('tags', '').split(','))

    # private property from delicious
    private = (a.get('private', '0') != '0')
      
    title = a.text or ''

    if url:

      try:
        ts = int(add_date)
        d = datetime.fromtimestamp(ts)
      except:
        d = datetime.now()

      new_pin(url, user_id, title=title, tags=tags, add_date=d, icon=icon, private=private)


