'''
Main
- runs methods (operations) for a given task (Flow)
'''

import numpy as np
import pandas as pd
import os
import re
import json
import requests
import argparse
import datetime

from py import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--flowname', help='Job name')
    parser.add_argument('--max_items', help='Number of items to process', default = 50)
    arguments = parser.parse_args().__dict__

    flowname  = arguments['flowname']
    # max_items  = arguments['max_items'] is hasattr(arguments, 'max_items') else None

    print("\n" + "=="* 5 + f" \t{datetime.datetime.now()}  \t{flowname}")

    classname = 'Flow'+ ''.join(word.title() for word in flowname.split('_'))
    klass = globals()[classname]
    params = {'flowtag' : True, 'mode' : 'dbquery', 'counting' : False, 'max_items': int(arguments['max_items'])}
    print(params)
    op = klass(**params)

    for operation in op.operations:
        if op.ok:
            getattr(op, operation)()
        else:
            print("nok", getattr(op, 'reason', ''), getattr(op, 'status_code', ''))
            break;

    op.execution_time()











# ----
