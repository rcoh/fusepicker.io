"""
A python library for accessing Filepicker.io
"""

import urllib, urllib2
import json
import cookielib
import uuid
from cookies import build_cookiejar

FP_API_KEY = "AOMWo29UpR4K4XuYWHG6Dz"
FP_HOSTNAME = "www.filepicker.io"
FP_BASEURL = "https://" + FP_HOSTNAME + "/"
REQUEST_CODE_AUTH = 600
REQUEST_CODE_GETFILE = 601
REQUEST_CODE_SAVEFILE = 602
REQUEST_CODE_GETFILE_LOCAL = 603

HOST_LIST = ['Dropbox', 'Facebook', 'Gmail']

link_table = {}
file_cache = {'/': {'is_dir': True}}

cj = cookielib.CookieJar()
build_cookiejar('.filepicker.io', cj)



def api_key_dict():
  return { 'app': {'apikey': FP_API_KEY} }

def js_session():
  return api_key_dict()

def js_session_mimetypes(mimetypes):
  base_dict = api_key_dict()
  base_dict['mimetypes'] = mimetypes
  return base_dict

def is_dir_del(data):
  return 'is_dir' in data and data['is_dir']
def update_cache(path, data):
  print 'caching ', path, 'is_dir:', is_dir_del(data)
  if path in file_cache:
    print 'previously: ', is_dir_del(file_cache[path])
  if not path in file_cache:
    file_cache[path] = {}

  #TODO: throw out content?

  if 'display_name' in data:
    data['display_name'] = safe_display_name(data['display_name'])
    
  file_cache[path] = dict(file_cache[path].items() + data.items())
  print 'after: ', is_dir_del(file_cache[path])
  if 'link_path' in data:
    link_table[path] = data['link_path']

def get_path_info(path, mimetypes):
  if path in link_table:
    path = link_table[path]
  else:
    print path, "not in cache. trying direct request"

  safe_path = urllib.quote_plus(path).replace('+', '%20')

  if not safe_path.endswith('/'):
    safe_path += '/'


  base_url = FP_BASEURL + "api/path" + safe_path 
  query = {'format': 'info', 'js_session':
      json.dumps(js_session_mimetypes(mimetypes)) }

  url = "%s?%s" % (base_url, urllib.urlencode(query))
  
  print "url: ", url
  return url

def safe_display_name(name):
  if name == "":
    return str(uuid.uuid1())
    
  return name.replace('/', """\/""")

def get_path_url(path):
  safe_path = urllib.quote_plus(path).replace('+', '%20')

  base_url = FP_BASEURL + "api/path" + safe_path 
  query = {'format': 'fpurl', 'js_session':
      json.dumps(js_session()) }

  url = "%s?%s" % (base_url, urllib.urlencode(query))
  return url

def get_response(path):
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
  r = opener.open(path)
  buf = r.read()
  try:
    data = json.loads(buf)
  except:
    print "failed parse. data was", buf, " Path was: ", path
    data = None
  return data


def data_for_dir(path):
  if path in file_cache and 'contents' in file_cache[path]:
    return file_cache[path]
  else:
    #TODO: mimetypes
    builturl = get_path_info(path, "")
    data = get_response(builturl)
    #if 'contents' in data and data['contents']:
    #  data['is_dir'] = True
    file_cache[path] = data
    return data_for_dir(path)

def url_for_file(path):
  return get_response(get_path_url(path))['url']

#### PUBLIC ####

def warm_cache():
  # Place the known hosts in the root
  contents = []
  for host in HOST_LIST:
    host_path = '/' + host
    host_dict = { 'is_dir': True, 'display_name': host }
    # Caches the host
    update_cache(host_path, host_dict)
    print file_cache['/' + host]
    data = data_for_dir(host_path)
    update_cache(host_path, data)
    data = dict(data)
    del data['contents']
    contents.append(host_dict)

  file_cache['/']['contents'] = contents  
  print file_cache['/']

def list_dir(path):
  data = data_for_dir(path)
  if not 'contents' in data:
    print "missing contents! Data:", data


  files = data['contents']
  print path, "Returning %d files" % len(files)
  update_cache(path, data)
  if not path.endswith('/'):
    path += '/'
  [update_cache(path + safe_display_name(f['display_name']), f) for f in files]
  return [safe_display_name(f['display_name']) for f in files]


def get_metadata(path):
  if path in file_cache:
    return file_cache[path]
  else:
    print "cache miss for: %s" % path
    return {}

