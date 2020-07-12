
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

from py import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--flowname', help='Job name')
    arguments = parser.parse_args().__dict__

    flowname  = arguments['flowname']

    print("\n" + "=="* 5 + f" \t{datetime.datetime.now()}  \t{flowname}")

    classname = 'Flow'+ ''.join(word.title() for word in flowname.split('_'))
    klass = globals()[classname]
    op = klass(flowtag = True, mode = 'dbquery', counting = False)
    for operation in op.operations:
        if op.ok:
            getattr(op, operation)()
        else:
            print("nok", getattr(op, 'reason', ''), getattr(op, 'status_code', ''))
            break;

    op.execution_time()











# ----
