#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The File Handle API provides simple interfaces for user to give ability to create/delete/list files.

    Examples to use:

    Create file: http://<api-endpoint>/file/create?name=test&username=myuser
    List files: http://<api-endpoint>/file/list?username=myuser
    Delete file: http://<api-endpoint>/file/delete?name=test&username=myuser
"""
import sys
import urllib
import time
import logging
import re
import tornado.options
from tornado.options import define, options
from tornado import ioloop, web, httpserver
from tornado.httpclient import HTTPRequest, HTTPClient, HTTPError
from pkg_resources import resource_filename, Requirement

LOG = logging.getLogger(__name__)
USERNAME_REGEX = r"^[a-zA-Z]{5,10}$"
FILENAME_REGEX = r"^[^.][a-z0-9]{1,14}$"

# Our files will be therer in format: user_filename
FILES_STORAGE= {}

class BaseHandler(web.RequestHandler):
    """Base Handler.. what to say more?"""
    def prepare(self):
        LOG.info(self.request)

        self.file_name = self.get_argument("name", '')
        self.user_name = self.get_argument("username", '')

class FileCreateHandler(BaseHandler):
    """Create File Handler
        Parameters:
            name - file name
            username - user name
    """
    def get(self):
        """Realization"""
        error = 0
        response_body = ""
        if not re.match(FILENAME_REGEX, self.file_name):
            self.set_status(400)
            response_body = "File Name not set or invalid"
            error = 1

        if not re.match(USERNAME_REGEX, self.user_name):
            self.set_status(400)
            response_body = "User Name not specified or invalid"
            error = 1

        if not error:
            FILES_STORAGE["{0}_{1}".format(self.user_name, self.file_name)] = 'ok'
            self.set_status(200)
            response_body = "OK"

        self.write(response_body)

class FileListHandler(BaseHandler):
    """File List Handler
        Parameters:
            username - user name
    """
    def get(self):
        """Realization"""
        error = 0
        response_body = ""

        if not re.match(USERNAME_REGEX, self.user_name):
            self.set_status(400)
            response_body = "User Name not specified or invalid"
            error = 1

        if not error:
            for user_file in FILES_STORAGE.keys():
                (uname, fname) = user_file.split("_", 1)
                if uname.startswith(self.user_name):
                    response_body += "{0}\n".format(fname)
            self.set_status(200)
        self.write(response_body)

class FileDeleteHandler(BaseHandler):
    """Delete File Handler
        Parameters:
            name - file name
            username - user name
    """
    def get(self):
        """Realization"""
        error = 0

        response_body = ""
        if not re.match(USERNAME_REGEX, self.user_name):
            self.set_status(400)
            response_body = "File Name not set or invalid"
            error = 1

        if not re.match(USERNAME_REGEX, self.user_name):
            self.set_status(400)
            response_body = "User Name not specified or invalid"
            error = 1

        deleted = 0
        if not error:
            for key in FILES_STORAGE.keys():
                (uname, fname) = key.split("_", 1)
                if fname == self.file_name:
                    del(FILES_STORAGE[key])
                    deleted = 1
                    break
            if deleted:
                self.set_status(200)
                response_body = "OK"
            else:
                self.set_status(404)
                response_body = "No such file"

        self.write(response_body)

def main():
    urlhandlers = [(r"http://[^/]+/file/create.*|/file/create.*", FileCreateHandler),
                    (r"http://[^/]+/file/list.*|/file/list.*", FileListHandler),
                    (r"http://[^/]+/file/delete.*|/file/delete.*", FileDeleteHandler)]
    if '-h' in sys.argv or '--help' in sys.argv:
        sys.argv.append('--help')
        print __doc__
        for url, handler in urlhandlers:
            print "URL:  %s" % url
            print "="*79
            print handler.__doc__
    define("port", type=int, default=8888, help="Server port. Default: 8888")
    define("address", type=str, default="0.0.0.0", help="Interface address to listed. Default: 0.0.0.0")
    define("h", type=bool, help="Help dammnit")
    define("v", type=bool, help="Verbose mode")
    tornado.options.parse_command_line()
    ts = web.Application(urlhandlers)

    server = httpserver.HTTPServer(ts, ssl_options=None)
    server.listen(options.port, options.address)
    if options.v:
        logging.info("Starting HTTPServer on *:%s" % options.port)
    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
