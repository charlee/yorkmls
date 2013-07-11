#!/usr/bin/env python

from lxml.html import fromstring

def import_house_task(user_id, url):

  import pdb; pdb.set_trace()
  html_string = open('data.html').read()

  if html_string:

    root = fromstring(html_string)

    body = [ e for e in root.getchildren() if e.tag.lower() == 'body' ]
    if len(body) > 0:
      body = body[0]

      tables = [ e for e in body.getchildren() if e.tag.lower() == 'table' ]

      for table in tables:
        print "table"






if __name__ == '__main__':
  import_house_task(0, '')
