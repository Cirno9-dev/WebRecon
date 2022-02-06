#!/usr/bin/env python3

from conf.config import *
import requests
requests.packages.urllib3.disable_warnings()

class Tool:
    def __init__(self):
        self.description = "Get headers of a website"
        self.options = {
            'url': {
                "value": "",
                "required": True,
                "description": "the target url (e.g. http://www.google.com)"
            }
        }
        self.output = {
            "status": "",
            "show": False,
            "data": ""
        }
    
    def run(self):
        data = {}
        print ('\n' + Y + '[!] Headers :' + W + '\n')
        try:
            r = requests.get(self.options["url"]["value"], verify=False, timeout=10)
            for k, v in r.headers.items():
                print (G + '[+]' + C + ' {} : '.format(k) + W + v)
                data.update({str(k): str(v)})
            print("")
            self.output['status'] = "success"
            self.output['data'] = data
        except Exception as e:
            print (R + '[-]' + C + ' Error : ' + W + str(e) + '\n')
            self.output['status'] = "fail"
            self.output['data'] = str(e)