#!/usr/bin/env python

from lxml.html import fromstring
from lxml import etree
import pickle
import re

def import_house_task(user_id, url):

  html_string = open('data.html').read()


  if html_string:

    root = fromstring(html_string)

    body = [ e for e in root.getchildren() if e.tag.lower() == 'body' ]
    if len(body) > 0:
      body = body[0]

      tables = [ e for e in body.getchildren() if e.tag.lower() == 'table' ]

      for table in tables:

        c = table.xpath('tr/td/table[2]')

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

          print pickle.dumps(images)
        else:
          images = []



if __name__ == '__main__':
  import_house_task(0, '')
