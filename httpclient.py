#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle, Jordan Ching
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
import urlparse
import ast

def help():
    print "httpclient.py [GET/POST] [URL] [ARGS]"
    print "ARGS must be an associative array (e.g \"{'a':'1','b':'something else')\")\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        s.connect((host, port))
        return s

    # takes in the raw headers, and returns the response code
    def get_code(self, data):
        headers = data.split("\n")
        responseStatus = headers[0].split(" ")
        return int(responseStatus[1])

    # takes in raw response, gets the part above the double line break (headers)
    def get_headers(self,data):
        response = data.split("\r\n\r\n")
        return response[0]

    # takes in raw response, gets the part below the double line break (body)
    def get_body(self, data):
        response = data.split("\r\n\r\n")
        return response[1]

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        sock.close()
        return str(buffer)

    def GET(self, url, args=None):
        urlInfo = urlparse.urlparse(url)
        port = urlInfo.port or 80
        path = urlInfo.path or "/"
        if(args != None):
            path = "%s?%s" % (path,urllib.urlencode(args))
        s = self.connect(urlInfo.hostname, port)
        
        s.sendall("GET %s HTTP/1.1\r\n" % path)
        s.sendall("Host: %s\r\n" % urlInfo.hostname)
        s.sendall("Accept: text/html\r\n")
        s.sendall("\r\n")
        
        response = self.recvall(s)
        headers = self.get_headers(response)
        code = self.get_code(headers)
        body = self.get_body(response)
        
        return HTTPRequest(code, body)

    def POST(self, url, args=None):
        urlInfo = urlparse.urlparse(url)
        port = urlInfo.port or 80
        path = urlInfo.path or "/"
        params = "" if args == None else urllib.urlencode(args)
        length = len(params)
        
        s = self.connect(urlInfo.hostname, port)
        
        s.sendall("POST %s HTTP/1.1\r\n" % path)
        s.sendall("Host: %s\r\n" % urlInfo.hostname)
        s.sendall("Content-Length: %s\r\n" % length)
        s.sendall("Content-Type: application/x-www-form-urlencoded\r\n")
        s.sendall("\r\n")
        s.sendall("%s\r\n" % params)
        
        response = self.recvall(s)
        headers = self.get_headers(response)
        code = self.get_code(headers)
        body = self.get_body(response)
        
        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    elif (len(sys.argv) == 4):
        args = ast.literal_eval(sys.argv[3])
        print client.command( sys.argv[2], sys.argv[1], args)
    else:
        print client.command( command, sys.argv[1] )    
