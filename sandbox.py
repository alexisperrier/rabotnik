
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
    flowname  = 'complete_videos'
    classname = 'Flow'+ ''.join(word.title() for word in flowname.split('_'))
    klass = globals()[classname]

    op = klass(flowtag = True, mode = 'dbquery', counting = True)
    for operation in op.operations:
        if op.ok:
            getattr(op, operation)()
        else:
            print("nok", op.reason,op.status_code)
            break;

    op.execution_time()





# ----
