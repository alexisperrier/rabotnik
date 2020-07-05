
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
    flowname  = 'video_stats'
    classname = 'Flow'+ ''.join(word.title() for word in flowname.split('_'))

    klass = globals()[classname]
    print(klass)
    op = klass(flowtag = True, mode = 'dbquery', counting = False)
    op.get_items()

    if op.flowtag:
        op.freeze()
    op.query_api()
    if op.ok:
        op.decode()
        op.prune()
        op.ingest()
    else:
        print("nok", op.reason)
    op.execution_time()





# ----
