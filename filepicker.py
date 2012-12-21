"""
A python library for accessing Filepicker.io
"""

import urllib, urllib2
import json
import cookielib
from cookies import build_cookiejar

FP_API_KEY = "YOURAPIKEY_HERE"
FP_HOSTNAME = "www.filepicker.io"
FP_BASEURL = "https://" + FP_HOSTNAME + "/"
REQUEST_CODE_AUTH = 600
REQUEST_CODE_GETFILE = 601
REQUEST_CODE_SAVEFILE = 602
REQUEST_CODE_GETFILE_LOCAL = 603

def api_key_dict():
  return { 'app': {'apikey': FP_API_KEY} }

def js_session():
  return api_key_dict()

def js_session_mimetypes(mimetypes):
  base_dict = api_key_dict()
  base_dict['mimetypes'] = mimetypes
  return base_dict

def get_path(path, mimetypes):
  safe_path = urllib.quote_plus(path)
  base_url = FP_BASEURL + "api/path" + safe_path 
  query = {'format': 'info', 'js_session':
      json.dumps(js_session_mimetypes(mimetypes)) }

  url = "%s?%s" % (base_url, urllib.urlencode(query))
  print "url: ", url
  return url
  
realurl = \
"""https://www.filepicker.io/api/path/Dropbox/6.01%20Design/?js_session=%257B%2522apikey%2522%253A%2522l5uQ3k7FQ5GoYCHyTdZV%2522%252C%2522mimetypes%2522%253A%255B%2522image%252F*%2522%255D%252C%2522persist%2522%253Afalse%252C%2522version%2522%253A%2522v1%2522%252C%2522storeLocation%2522%253Anull%257D&format=info"""

builturl = get_path("/Dropbox/", "")

cj = cookielib.CookieJar()
build_cookiejar('.filepicker.io', cj)
print cj
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
r = opener.open(builturl)
print r.read()
