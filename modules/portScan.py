#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from matplotlib.pyplot import cla
from conf.config import *
import socket
import threading
from queue import Queue

PortScanData = {}
class Tool:
    def __init__(self):
        self.description = "A tool to scan the target's ports"
        self.options = {
            'ip': {
                "value": "",
                "required": True,
                "description": "the target's ip address (e.g. 169.192.1.1)"
            },
            'ports': {
                "value": "1-1000",
                "required": True,
                "description": "the ports to scan (e.g. 80,8080,443 or 1-65535)"
            },
            'threads': {
                "value": "10",
                "required": False,
                "description": "the number of threads to use (e.g. 10)"
            }
        }
        self.output = {
            "status": "",
            "data": "",
            "save": True
        }
    
    def run(self):
        global PortScanData
        print('\n' + Y + '[!]' + Y + ' Starting Port Scan...' + W + '\n')
        
        threads = []
        tNum = threadNum if self.options["threads"]["value"] == "" else int(self.options["threads"]["value"])
        queue = Queue()
        try:
            ip = self.options["ip"]["value"]
            # process the ports
            ports = self.options["ports"]["value"]
            if "-" in ports:
                for port in range(int(ports.split("-")[0]), int(ports.split("-")[1]) + 1):
                    queue.put(port)
            else:
                for port in ports.split(","):
                    queue.put(int(port))
            # create threads
            for _ in range(tNum):
                t = MyThread(queue, ip)
                t.daemon = True
                threads.append(t)
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            # success
            print("")
            self.output['status'] = "success"
            self.output['data'] = PortScanData
        except Exception as e:
            print(R + '[-]' + C + ' Error : ' + W + str(e) + '\n')
            self.output['status'] = "fail"
            self.output['data'] = str(e)
            
class MyThread(threading.Thread):
    def __init__(self,queue, ip):
        threading.Thread.__init__(self)
        self.queue = queue
        self.ip = ip
        
    def run(self):
        global PortScanData
        while not self.queue.empty():
            port = self.queue.get()
            # tcp
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.ip, port))
                s.close()
                # check the service if it's open
                try:
                    service = socket.getservbyport(port, 'tcp')
                    print(G + '[+] ' + C + (str(port)+"/tcp").ljust(11) + W + service.ljust(9))
                    PortScanData.update({str(port): service})
                except:
                    print(G + '[+] ' + C + (str(port)+"/tcp").ljust(11) + W + "unknown".ljust(9))
                    PortScanData.update({str(port): "unknown"})
                continue
            except Exception as e:
                pass
            # udp
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(3)
                s.connect((self.ip, port))
                s.close()
                # check the service if it's open
                try:
                    service = socket.getservbyport(port, 'udp')
                    print(G + '[+] ' + C + (str(port)+"/udp").ljust(11) + W + service.ljust(9))
                    PortScanData.update({str(port): service})
                except:
                    print(G + '[+] ' + C + (str(port)+"/udp").ljust(11) + W + "unknown".ljust(9))
                    PortScanData.update({str(port): "unknown"})
                continue
            except Exception as e:
                pass