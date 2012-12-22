import sqlite3
import cookielib
import urllib2
#TODO: make semi-portable
CHROME_PATH = '/home/rcoh/.config/chromium/Default/Cookies'

con = sqlite3.connect(CHROME_PATH)
cur = con.cursor()

def build_cookiejar(site_name, cj):
  cookies = cur.execute("""select name,value,path,
      host_key,expires_utc,secure,httponly,last_access_utc,
      persistent from cookies where host_key='%s'
      """ % site_name).fetchall()
  for cookie in cookies:
    c = cookielib.Cookie(0, cookie[0], cookie[1], None, False,
        cookie[3], cookie[3].startswith('.'), cookie[3].startswith('.'),
        cookie[2], False,
        cookie[5],
        cookie[4], cookie[4] == "",
        None, None, {})
#    print c
    if cookie[0] == "session":
      cj.set_cookie(c)

    
