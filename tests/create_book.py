# -*- coding: utf-8 -*-
import os
import json
import ConfigParser
import string

config=ConfigParser.ConfigParser()
config.read('book.dat')

def create_book():
    for section in config.sections():
        for option in config.options(section):
            body = {
                "name": config.get(section,option)
            }

            cmd = "curl -X POST localhost:7777/v1/user/%s/book -d '%s'"% (section[-1],json.dumps(body))
            print cmd
            os.system(cmd)

create_book()
