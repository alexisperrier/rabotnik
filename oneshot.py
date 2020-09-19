'''

Works like sandbox.py
- instantiate flow
- define op.sql before calling op.get_items()
'''

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
    # job.config['offset_factor'] = 0

    params = {'flowtag' : True, 'mode' : 'local', 'counting' : False, 'max_items': 50}
    op = klass(**params)
    # for ci.collection_id in (13,15,20)
    op.sql = '''
             select v.video_id
             from video v
             join channel ch on ch.channel_id = v.channel_id
             join collection_items ci on ch.channel_id = ci.channel_id
             left join flow as fl on fl.video_id = v.video_id and fl.flowname = 'video_stats'
             left join video_stat vs on (vs.video_id = v.video_id)
             where  fl.id is null
                and vs.id is null
                and ci.collection_id in (15)
                limit 50
    '''

    # op.get_items()
    # op.freeze()
    # op.query_api()
    # op.decode()
    # op.prune()
    # op.ingest()
    # op.bulk_release()

    for operation in op.operations:
        start_time = datetime.datetime.now()
        # print("== --",operation)
        if op.ok:
            getattr(op, operation)()
        else:
            print("nok", getattr(op, 'reason', ''), getattr(op, 'status_code', ''))
            break;
        delta_time = (datetime.datetime.now() - start_time).seconds
        # print("--",operation,f"execution time {delta_time}s")

    op.execution_time()




    # ----
