
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

from pathlib import Path

if __name__ == '__main__':

    channel_id = 'UCu0zi8f_k5emuPLbLyUh6MA'

    sql = f'''
        select title || ' ' || description as channel_text from channel where channel_id = '{channel_id}'
    '''
    job.execute(sql)
    channel_text = job.db.cur.fetchone()[0]



    # flowname  = 'feed_parsing'
    # classname = 'Flow'+ ''.join(word.title() for word in flowname.split('_'))
    # klass = globals()[classname]
    #
    # op = klass(flowtag = True, mode = 'local', counting = False)
    # for operation in op.operations:
    #     print("--",operation)
    #     if op.ok:
    #         getattr(op, operation)()
    #     else:
    #         print("nok", op.reason,op.status_code)
    #         break;
    #
    # op.execution_time()





# ----
