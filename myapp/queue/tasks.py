from . import queue_task, get_tmp_param

import urllib2

import re
from lxml import etree
from lxml.html import fromstring
from datetime import datetime
from core.models import User
from core.house import new_house


@queue_task
def import_houses_task(user_id, url):

  html_string = urllib2.urlopen(url).read()

  if html_string:

    root = fromstring(html_string)

    body = [ e for e in root.getchildren() if e.tag.lower() == 'body' ]
    if len(body) > 0:
      body = body[0]

      tables = [ e for e in body.getchildren() if e.tag.lower() == 'table' ]

      for table in tables:

        address = table.xpath('tr/td/table[2]/tr/td[2]/table/tr[1]/td')[0].text_content().replace(u"\xa0", " ")
        town = table.xpath('tr/td/table[2]/tr/td[2]/table/tr[2]/td')[0].text_content().replace(u"\xa0", " ")
        price = table.xpath('tr/td/table[2]/tr/td[2]/table/tr[1]/td[2]')[0].text_content().replace(u"\xa0", " ")
        mls_id = table.xpath('tr/td/table[2]/tr[3]/td/table/tr/td')[0].text_content().replace(u"\xa0", " ").strip()
        script_element = table.xpath('tr/td/table[2]/tr/td[1]/div/script')
        if script_element:
          script = script_element[0].text_content()
          images = re.search(r'new Array\(([^)]*)\)', script).group(1).split(',')
          images = map(lambda x:x.replace("'", ''), images)

          image0 = table.xpath('tr/td/table[2]/tr/td[1]/div/img[1]/@src')[0]
          images[0] = str(image0)
        else:
          images = []

        new_house(mls_id, user_id, address, town, images, price, etree.tostring(table))

        
