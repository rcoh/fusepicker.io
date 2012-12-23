"""
A python library for accessing Filepicker.io
"""

import urllib, urllib2
import json
import cookielib
from cookies import build_cookiejar

FP_API_KEY = "apikey2"
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
  safe_path = urllib.quote_plus(path).replace('+', '%20')
  if not safe_path.endswith('/'):
    safe_path += '/'
  base_url = FP_BASEURL + "api/path" + safe_path 
  query = {'format': 'info', 'js_session':
      json.dumps(js_session_mimetypes(mimetypes)) }

  url = "%s?%s" % (base_url, urllib.urlencode(query))
  
  print "url: ", url
  return url

path_cache = {}
file_cache = {}
def data_for_dir(path):
  if path in path_cache:
    return path_cache[path]
  else:
    #TODO: mimetypes
    #TODO: memoize / cache
    builturl = get_path(path, "")
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    r = opener.open(builturl)
    path_cache[path] = json.loads(r.read())
    return data_for_dir(path)


cj = cookielib.CookieJar()
build_cookiejar('.filepicker.io', cj)
#### PUBLIC ####
def list_dir(path):
  if path == "/":
    list_dir('/Dropbox')
    list_dir('/Facebook')
    root = {'is_dir': True, 'filename': ''}
    update_cache("/", root)
    return ["Dropbox", "Facebook"]
  path = path
  data = data_for_dir(path)
  if not 'contents' in data:
    print "missing contents!", data

  files = data['contents']
  root_data = dict(data)
  root_data['is_dir'] = True
  del root_data['contents']
  file_cache[path] = root_data
  print path, "Returning %d files" % len(files)
  [update_cache(path, f) for f in files]
  return [f['display_name'] for f in files]

def update_cache(path, f):
  if not path.endswith('/'):
    path += '/'
  if 'display_name' in f:
    path += f['display_name']
  else:
    path += f['filename']
  file_cache[path] = f

def get_metadata(path):
  if path == "/":
    return {'is_dir': True, 'filename': ''}
  if path in file_cache:
    print "cache hit"
    return file_cache[path]
  else:
    print "cache miss for: %s" % path
#    print file_cache
#    import pdb; pdb.set_trace()
    return {}

