# memoizing proxy
a small forward proxy to serve the http requests from local files - local data created on first request with the content retrieved from the remote url

Note: once the local file is created it won't be updated as the main purpose of this proxy was to get consistent results when running the automated (xslt&xquery) tests that are accessing remote files (schemas, dtds, images, etc.)

* store the uri->local file name mappings in a dictionary
 - load to memory from a json file on program start; if the file doesn't exists an empty dictionary is created
* on a http request the url is remapped to a local file name
 - from the dictionary either an existing mapping is retrieved or a new one is created from the (uri, len(dictionary)) tuple
* if a local file doesn't exists then a new one is created with the content is retrieved from the remote location or empty if there was an error
* finally the GET request is served from the local file content or with error 404 if the file is empty
