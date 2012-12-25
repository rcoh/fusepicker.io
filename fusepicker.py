#!/usr/bin/env python

from sys import argv, exit
from time import time

from errno import ENOENT
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn


import filepicker
from stat import S_IFDIR, S_IFREG

import urllib2

class FilePicker(LoggingMixIn, Operations):
  def __init__(self, path='.'):
    filepicker.warm_cache()
    self.data_cache = {}

  def chmod(self, path, mode):
    pass

  def chown(self, path, uid, gid):
    pass

  def create(self, path, mode):
    print "create called"

  def destroy(self, path):
    pass

  def getattr(self, path, fh=None):
    data = filepicker.get_metadata(path)
    dirm = S_IFDIR | 755
    filem = S_IFREG | 444
    if data:
      if not 'is_dir' in data:
        print 'no is_dir for ', path
        mode = filem
      else:
        mode = dirm if data['is_dir'] else filem
    else:
      raise FuseOSError(ENOENT)


    return {'st_atime': 0, 'st_gid': 1000, 'st_mode': mode, 'st_uid':
        1000, 'st_size': 1000 }

  def mkdir(self, path, mode):
    pass

  def read(self, path, size, offset, fh):
    if path in self.data_cache:
      (old_offset, data) = self.data_cache[path]
    else:
      url = filepicker.url_for_file(path)
      print "url to download from: ", url
      f = urllib2.urlopen(url)
      # TODO: cache data
      data = f.read()
      old_offset = 0
      self.data_cache[path] = (old_offset, data)

    offset += old_offset
    print "requesting", path, "offset:", offset, "size:", size, "real len:", len(data)
    start = min(len(data), offset)
    end = min(len(data), offset+size)
    print "start", start, "end", end
    offset += end - start
    self.data_cache[path] = (offset, data)

    return data[start:end]

  def readdir(self, path, fh):
    ret = ['.', '..'] + [name.encode('utf-8') for name in
        filepicker.list_dir(path)]
    return ret 

  def readlink(self, path):
    print "READLINK"
  
  def rename(self, old, new):
    pass

  def rmdir(self, path):
    pass

  def symlink(self, target, source):
    pass

  def truncate(self, path, length, fh=None):
    pass

  def unlink(self, path):
    pass

  def utimens(self, path, times=None):
    pass

  def write(self, path, data, offset, fh):
    print "write called"


if __name__ == '__main__':
  if len(argv) != 2:
    print('usage: %s <mountpoint>' % argv[0])
    exit(1)

  fuse = FUSE(FilePicker(), argv[1], foreground=True, nothreads=True)
