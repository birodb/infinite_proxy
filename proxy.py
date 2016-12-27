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
import base64
#import zlib
import hashlib

PORT = 8080
BASE_PATH = os.path.abspath('proxy_cache')

def ensure_dir(dir_name):
    """create dir if doesn't exists"""
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

class Proxy(http.server.SimpleHTTPRequestHandler):
    """the caching proxy class"""
    def as_local_path(self):
        """convert the url to a local file path"""
        #return os.path.join(BASE_PATH, urllib.parse.quote_plus(self.path))
        bin_data = self.path.encode('UTF-8')
        #compr_data = zlib.compress(bin_data, 9)
        compr_data = hashlib.sha256(bin_data).digest()
        local_name = base64.urlsafe_b64encode(compr_data).decode('ASCII')
        local_name = local_name.split("=")[0]
        return os.path.join(BASE_PATH, local_name)

    def do_GET(self):
        """handle the GET request"""
        local_fname = self.as_local_path()
        if not os.path.isfile(local_fname):
            #file doesn't exists, create it
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
    print("serving at port: ", PORT, " base path ", BASE_PATH)
    httpd = socketserver.ForkingTCPServer(('', PORT), Proxy)
    httpd.serve_forever()
