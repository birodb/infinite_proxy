# infinite_proxy
a small forward proxy to serve the http requests from local files - local file created with content retrieved from the remote url on first request

Note: once the local file is created it won't be updated as the main purpose of this proxy was to get consistent results when running the automated (xslt&xquery) tests that are accessing remote files (schemas, dtds, images, etc.)

* the url is remapped to a local path; tried several approaches for converting the remote url to a local file name:
 - urllib.parse.quote_plus - failed for long urls - ex. a google maps location with a long query string
 - zlib.compression + base64 - unique, but found still too long 
 - sha256 + base64 - can take the risk of hash collisions and switch back to zip if needed
* if there is no local file, then it's created and filled with the content retrieved from the original url
* if there was an error retrieving the data from the remote url, then a zero length file is created
* finally the GET request is served from the local file or with error 404 if the file doesn't exist or is empty
