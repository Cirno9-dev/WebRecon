#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from conf.config import *
import dnslib

class Tool:
    def __init__(self):
        self.description = "dns lookup"
        self.options = {
            'domain': {
                "value": "",
                "required": True,
                "description": "the target domain (e.g. google.com)"
            },
            "dnsIP": {
                "value": "8.8.8.8",
                "required": True,
                "description": "the dns server to get the dns"
            },
            "dnsPort": {
                "value": "53",
                "required": True,
                "description": "the dns server port to get the dns"
            }
        }
        self.output = {
            "status": "",
            "show": False,
            "data": ""
        }
    
    def run(self):
        data = {"dns": [], "dmarc": []}
        print('\n' + Y + '[!]' + Y + ' Starting DNS Enumeration...' + W + '\n')
        try:
            # dns
            types = ['A', 'AAAA', 'ANY', 'CAA', 'CNAME', 'MX', 'NS', 'TXT']
            ansList = []
            for type in types:
                q = dnslib.DNSRecord.question(self.options['domain']['value'], qtype=type)
                pkt = q.send(self.options['dnsIP']['value'], int(self.options['dnsPort']['value']), tcp="UDP")
                ans = dnslib.DNSRecord.parse(pkt)
                ans = str(ans)
                ans = ans.split('\n')
                ansList.extend(ans)
            ansList = set(ansList)
            
            for entry in ansList:
                if entry.startswith(';') == False:
                    print(G + '[+] ' + W + str(entry))
                    data['dns'].append(str(entry))
            if len(data['dns']) == 0:
                print(R + '[-] ' + C + 'No DNS Records Found' + W)
            
            # dmarc
            q = dnslib.DNSRecord.question('_dmarc.'+self.options['domain']['value'], qtype=type)
            pkt = q.send(self.options['dnsIP']['value'], int(self.options['dnsPort']['value']), tcp="UDP")
            dmarcAnsList = dnslib.DNSRecord.parse(pkt)
            dmarcAnsList = str(dmarcAnsList)
            dmarcAnsList = dmarcAnsList.split('\n')
            
            for entry in dmarcAnsList:
                if entry.startswith(';') == False:
                    print(G + '[+] ' + W + str(entry))
                    data['dmarc'].append(str(entry))
            if len(data['dmarc']) == 0:
                print("\n" + R + '[-] ' + C + 'No DMARC Records Found' + W)
            print("")
                
            self.output['status'] = "success"
            self.output['data'] = data
        except Exception as e:
            print(R + '[-]' + C + ' Error : ' + W + str(e) + '\n')
            self.output['status'] = "fail"
            self.output['data'] = str(e)
        