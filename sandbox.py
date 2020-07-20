
# NEXT
# -- translate channel_stat into ChannelStat and instantiate class name
# -- test on 50 channels

import numpy as np
import pandas as pd
import os
import re
import json
import requests
import argparse
import datetime
from tqdm import tqdm
from py import *

from pathlib import Path

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--flowname', help='Job name')
    parser.add_argument('--max_items', help='Number of items to process', default = 50)
    arguments = parser.parse_args().__dict__

    flowname  = arguments['flowname']
    print("\n" + "=="* 5 + f" \t{datetime.datetime.now()}  \t{flowname}")
    classname = 'Flow'+ ''.join(word.title() for word in flowname.split('_'))
    klass = globals()[classname]

    params = {'flowtag' : True, 'mode' : 'local', 'counting' : True, 'max_items': int(arguments['max_items'])}
    print(params)
    op = klass(**params)

    raise "stop"

    for operation in op.operations:
        start_time = datetime.datetime.now()
        print("--",operation)
        if op.ok:
            getattr(op, operation)()
        else:
            print("nok", op.reason,op.status_code)
            break;
        delta_time = (datetime.datetime.now() - start_time).seconds
        print("--",operation,f"execution time {delta_time}s")

    op.execution_time()





# ----
