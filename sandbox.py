
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


    flowname  = 'video_scrape'
    classname = 'Flow'+ ''.join(word.title() for word in flowname.split('_'))
    klass = globals()[classname]

    op = klass(flowtag = True, mode = 'local', counting = True)
    # op.get_items()
    # op.freeze()
    # op.request_pages()
    # op.parse()
    # op.ingest()
    # op.postop()


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
