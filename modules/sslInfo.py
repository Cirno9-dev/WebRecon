#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from conf.config import *
import ssl
import socket
import os

class Tool:
    def __init__(self):
        self.description = "Get the SSL certificate information"
        self.options = {
            'domain': {
                "value": "",
                "required": True,
                "description": "The target domain (e.g. google.com)"
            },
            'sslPort': {
                "value": "443",
                "required": True,
                "description": "Specify SSL Port (e.g. 443)"
            }
        }
        self.output = {
            "status": "",
            "data": "",
            "save": True
        }
    
    def run(self):
        self._result = {}
        self._pair = {}
        hostname = self.options["domain"]["value"]
        sslp = int(self.options["sslPort"]["value"])
        print ('\n' + Y + '[!]' + Y + ' SSL Certificate Information : ' + W + '\n')
        try:
            # check the ssl port
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.connect((hostname, sslp))
            s.close()
            
            # get the ssl certificate
            ctx = ssl.create_default_context()
            s = socket.socket()
            s.settimeout(10)
            sslSock = ctx.wrap_socket(s, server_hostname=self.options["domain"]["value"])
            try:
                sslSock.connect((hostname, sslp))
                info = sslSock.getpeercert()
            except Exception as e:
                info = ssl.get_server_certificate((hostname, sslp))
                f = open('{}.pem'.format(hostname), 'w')
                f.write(info)
                f.close()
                cert_dict = ssl._ssl._test_decode_cert('{}.pem'.format(hostname))
                info = cert_dict
                os.remove('{}.pem'.format(hostname))
            
            # process the ssl info
            for k, v in info.items():
                if isinstance(v, tuple):
                    self.unpack(v)
                    for k, v in self._pair.items():
                        print(G + '[+]' + C + ' {} : '.format(str(k)) + W + str(v))
                        self._result.update({str(k): str(v)})
                    self._pair.clear()
                else:
                    print(G + '[+]' + C + ' {} : '.format(str(k)) + W + str(v))
                    self._result.update({str(k): str(v)})
            
            print("")
            self.output['status'] = "success"
            self.output['data'] = self._result
        except Exception as e:
            print (R + '[-]' + C + ' Error : ' + W + str(e) + '\n')
            self.output['status'] = "fail"
            self.output['data'] = str(e)
    
    # unpack the tuple
    def unpack(self, v):
        convert = False
        for item in v:
            if isinstance(item, tuple):
                for subitem in item:
                    if isinstance(subitem, tuple):
                        for elem in subitem:
                            if isinstance(elem, tuple):
                                self.unpack(elem)
                            else:
                                convert = True
                        if convert == True:
                            self._pair.update(dict([subitem]))
            else:
                print(G + '[+]' + C + ' {} : '.format(str(v)) + W + str(item))
                self._result.update({str(v): str(item)})