#!/usr/bin/env python

## Tiny Syslog Server in Python.
##
## This is a tiny syslog server that is able to receive UDP based syslog
## entries on a specified port and save them to a file.
## That's it... it does nothing else...
## There are a few configuration parameters.

HOST, PORT = "0.0.0.0", 514

import os
import json
import logging
import socketserver
from datetime import datetime
from elasticsearch import Elasticsearch

es = Elasticsearch([os.environ.get('ES_HOST')],
  http_auth=(os.environ.get('ES_USER'),os.environ.get('ES_PASS')),
  scheme="http",
  port=os.environ.get('ES_PORT')
)

class SyslogUDPHandler(socketserver.BaseRequestHandler):

  def handle(self):
    skel = { }

    data = bytes.decode(self.request[0].strip())
    socket = self.request[1]
    
    boo = str(data).split()

    skel['month'] = boo.pop(0)
    skel['day'] = boo.pop(0)
    skel['time'] = boo.pop(0)
    skel['hostname'] = boo.pop(0)
    skel['app'] = boo.pop(0)
    skel['action'] = boo.pop(0)

    if skel['action'] == "DROP" or skel['action'] == "ACCEPT":
      for x in boo:
        if len(x.split('=')) == 2:
          key,val = x.split("=")
          key = key.lower()
          skel[key] = val
        else:
          x = x.lower()
          skel[x] = ''

    print(json.dumps(skel, indent=4, sort_keys=True))
    upload(skel)


def upload(doc):
  now = datetime.now()
  doc['timestamp'] = now

  index = 'router-' + str(now.year) + '.' + str(now.month) + '.' + str(now.day)
  res = es.index(index=index, body=doc)
  print(res['result'])


if __name__ == "__main__":

  try:
    server = socketserver.UDPServer((HOST,PORT), SyslogUDPHandler)
    server.serve_forever(poll_interval=0.5)
  except (IOError, SystemExit):
    raise
  except KeyboardInterrupt:
    print ("Crtl+C Pressed. Shutting down.")
