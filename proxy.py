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
    def __init__(self, *args, **kwargs):
        super(Proxy, self).__init__(*args, **kwargs)
        self.protocol_version = 'HTTP/1.1'

    def setup(self):
        print("init connection")
        self.timeout = 3
        http.server.SimpleHTTPRequestHandler.setup(self)
        #self.rfile._sock.settimeout(10)
        

    def wants_file(self, local_fname):
        if not os.path.isfile(local_fname):
            #file doesn't exists, create it
            NAME_MAP.save()
            #print("caching: ", self.path, local_fname)
            try:
                with open(local_fname, "wb") as f_cache:
                    with urllib.request.urlopen(self.path) as f_in:
                        shutil.copyfileobj(f_in, f_cache)
            except urllib.error.HTTPError as e:
                #print("http-error: ", e)
                pass
            except urllib.error.URLError as  e:
                #print("url-error: ", e)
                pass
            except Exception as e:
                #print("other-error: ", e)
                pass

    def get_or_head(self, wants_data):
        #print(self.path)
        local_fname = NAME_MAP.as_local(self.path)
        self.wants_file(local_fname)
        #self.protocol_version = 'HTTP/1.1'
        try:
            local_fsize = os.path.getsize(local_fname)
            if local_fsize:
                #print("serving locally:", local_fname, self.path)
                self.send_response(200)
                self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Length', '{}'.format(local_fsize))
                self.end_headers()
                with open(local_fname, "rb") as f_in:
                    #self.copyfile(f_in, self.wfile)
                    if wants_data:
                        self.copyfileobj(f_in, self.wfile)
                    #self.send_response(200)
                    #self.end_headers()
            else:
                raise Exception("error retrieving content "+self.path)
        except Exception as e:
            print("other-error: ", str(e))
            self.send_error(404)
        return

    def do_GET(self):
        """handle the GET request"""
        self.get_or_head(True)

    def do_HEAD(self):
        #print('wants head', self.path)
        self.get_or_head(False)

if __name__ == "__main__":
    try:
        ensure_dir(BASE_PATH)
        NAME_MAP.load()

        print("serving at port: ", PORT, " base path ", BASE_PATH)
        httpd = socketserver.TCPServer(('', PORT), Proxy)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('got Ctrl-C')
        httpd.socket.close() 
