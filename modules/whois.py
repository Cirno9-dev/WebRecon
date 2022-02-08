#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from conf.config import *
import ipwhois

class Tool:
    def __init__(self):
        self.description = "Whois lookup"
        self.options = {
            'ip': {
                "value": "",
                "required": True,
                "description": "IP address to lookup (e.g. 169.192.1.1)"
            }
        }
        self.output = {
            "status": "",
            "data": "",
            "save": True
        }
    
    def run(self):
        data = {}
        print ('\n' + Y + '[!]' + Y + ' Whois Lookup : ' + W + '\n')
        try:
            lookup = ipwhois.IPWhois(self.options['ip']['value'])
            results = lookup.lookup_whois()
            # process whois results
            for k, v in results.items():
                if v != None:
                    if isinstance(v, list):
                        for item in v:
                            for i, j in item.items():
                                if j != None:
                                    print (G + '[+]' + C + ' '+ str(i) + ' : ' + W + str(j).replace(',', ' ').replace('\r', ' ').replace('\n', ' '))
                                    data.update({str(i): str(j).replace(',', ' ').replace('\r', ' ').replace('\n', ' ')})
                                else:
                                    pass
                    else:
                        print (G + '[+]' + C + ' ' + str(k) + ' : ' + W + str(v).replace(',', ' ').replace('\r', ' ').replace('\n', ' '))
                        data.update({str(k): str(v).replace(',', ' ').replace('\r', ' ').replace('\n', ' ')})
                else:
                    pass
            print("")
            self.output['status'] = "success"
            self.output['data'] = data
        except Exception as e:
            print(R + '[-]' + C + ' Error : ' + W + str(e) + '\n')
            self.output['status'] = "fail"
            self.output['data'] = str(e)