# infinite_proxy
a small forward proxy to serve the http requests from local files - created and data retrieved from remote url on first request

needed to get consistent results when running the automated (xslt&xquery) tests

* the url is remapped to a local path
 tried several approaches for converting the remote url to a local file 
 - urllib.parse.quote_plus - failed for long urls - ex. a google maps location query string
 - zlib.compression + base64 - unique though found still too long
 - sha256 + base64 - guess can take the risk of hash collisions  -if there is no file at the target location, then it's retrieved and saved from the remote url
* if there was an error retrieving the data from the remote url, then a zero length file is created
* get request is served from the local file or with error 404 if the file doesn't exist or is empty
