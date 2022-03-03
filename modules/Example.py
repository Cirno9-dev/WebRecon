#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# include the config
from conf.config import *

# The class Name must be Tool
class Tool:
    def __init__(self):
        # description of the tool
        self.description = "Description of the tool"
        # options of the tool
        # key: option name
        # value: {"value": "", "required": True, "description": "Description of the option"}
        # value: value of the option
        # required: True if the option is required
        # description: description of the option
        self.options = {
            'arg1': {
                "value": "",
                "required": True,
                "description": "Description of arg1"
            },
            'arg2': {
                "value": "",
                "required": False,
                "description": "Description of arg2"
            }
        }
        # output of the tool
        # status: success or fail
        # data: output data, recommended to use dict
        # save: True if you want to save the output to a file
        self.output = {
            "status": "",
            "data": "",
            "save": True
        }
    
    # run the tool
    def run(self):
        pass