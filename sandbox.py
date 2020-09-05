
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

    flowname  = 'video_stats'
    classname = 'Flow'+ ''.join(word.title() for word in flowname.split('_'))
    klass = globals()[classname]
    job.config['offset_factor'] = 0

    params = {'flowtag' : False, 'mode' : 'local', 'counting' : True, 'max_items': 10}
    op = klass(**params)
    # op.get_items()
    # op.freeze()
    # op.query_api()
    # op.decode()
    # op.ingest()


    # op.query_api()
    # op.ingest()
    # op.ingest_collections()

    for operation in op.operations:
        start_time = datetime.datetime.now()
        print("== --",operation)
        if op.ok:
            getattr(op, operation)()
        else:
            print("nok", getattr(op, 'reason', ''), getattr(op, 'status_code', ''))
            break;
        delta_time = (datetime.datetime.now() - start_time).seconds
        print("--",operation,f"execution time {delta_time}s")

    op.execution_time()

# ------------






# ----
