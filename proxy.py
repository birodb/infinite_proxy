#!/usr/bin/python3
"""module to implement a local http proxy caching the requests infinitely"""
import socketserver
import http.server
import urllib.request
import urllib.parse
import urllib.error
import os
import os.path
import shutil
import json

PORT = 8080
BASE_PATH = os.path.abspath('proxy_cache')
def ensure_dir(dir_name):
    """create dir if doesn't exists"""
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

def abs_path(fname):
    """convert to abs path relative to base path"""
    return os.path.join(BASE_PATH, fname)

class NameMap:
    def __init__(self, fname):
        self.data = {}
        self.fname = fname

    def load(self):
        try:
            with open(self.fname, "rt") as f:
                self.data = json.load(f)
        except (IOError) as e:
            print("proxy cache file not exists yet")

    def save(self):
        with open(self.fname, "w+t") as f:
            json.dump(self.data, f, indent=2, sort_keys=True)
    
    def as_local(self, path):
        """remap the http uri to a local file(number)"""
        return abs_path(self.data.setdefault(path, str(len(self.data))))

NAME_MAP = NameMap(abs_path('proxy.json'))
        
class Proxy(http.server.SimpleHTTPRequestHandler):
    """the caching proxy class"""

    def do_GET(self):
        """handle the GET request"""
        local_fname = NAME_MAP.as_local(self.path)
        if not os.path.isfile(local_fname):
            #file doesn't exists, create it
            NAME_MAP.save()
            print("caching: ", self.path, local_fname)
            try:
                with open(local_fname, "wb") as f_cache:
                    with urllib.request.urlopen(self.path) as f_in:
                        shutil.copyfileobj(f_in, f_cache)
            except urllib.error.HTTPError as e:
                print("http-error: ", e)
            except urllib.error.URLError as  e:
                print("url-error: ", e)
            except Exception as e:
                print("other-error: ", e)

        try:
            if os.path.getsize(local_fname):
                print("serving locally:", local_fname, self.path)
                with open(local_fname, "rb") as f_in:
                    self.copyfile(f_in, self.wfile)
            else:
                raise Exception("error retrieving content "+self.path)
        except Exception as e:
            print("other-error: ", e)
            self.send_error(404, str(e))


if __name__ == "__main__":
    ensure_dir(BASE_PATH)
    NAME_MAP.load()

    print("serving at port: ", PORT, " base path ", BASE_PATH)
    httpd = socketserver.TCPServer(('', PORT), Proxy)
    httpd.serve_forever()
