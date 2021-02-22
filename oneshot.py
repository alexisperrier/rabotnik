'''
oneshot script for one shot operations
Works like sandbox.py
- instantiate flow
- define op.sql before calling op.get_items()
'''

import numpy as np
import pandas as pd
import json, csv, re, json, sys
import requests
import argparse
import datetime
from tqdm import tqdm
from py import *

from pathlib import Path
import glob

if __name__ == '__main__':

    # read channel list from csv
    data_path = "/Users/alexis/amcp/CNCDH/data/cncdh_channels_20201222.csv"
    df = pd.read_csv(data_path)

    channel_ids = df.channel_id.values
    data = []
    k = 0
    for channel_id in channel_ids:

        # get video_ids for that channel
        sql = f"select video_id from video where channel_id = '{channel_id}'"
        job.execute(sql)
        video_ids = [r[0] for r in  job.db.cur.fetchall()]
        video_count = len(video_ids)

        sql = f'''
            select count(*) from video_recommendations where tgt_video_id in ('{"','".join(video_ids)}')
        '''
        job.execute(sql)
        target_count = job.db.cur.fetchone()[0]

        sql = f'''
            select distinct(src_video_id)  from video_recommendations where src_video_id in ('{"','".join(video_ids)}')
        '''
        job.execute(sql)

        source_count = len([r[0] for r in  job.db.cur.fetchall()])

        data.append({
            "channel_id": channel_id,
            "channel_video_count": video_count,
            "recommended_count": target_count,
            "videos_as_source": source_count,
        })
        if k % 100 ==0:
            print(f"------------------------------------- \tsource \tchannel\ttarget\tratio")
        if video_count> 0:
            print(f"{k:>3}/{len(channel_ids):4} [{channel_id}] {source_count:4} \t{video_count:4} \t{target_count:4} \t{np.round(target_count/ video_count,2)}")
        else:
            print(f"{k:>3}/{len(channel_ids):4} [{channel_id}] {source_count:4} \t==== \t{target_count:4}")

        k+=1
    data = pd.DataFrame(data)




    # for each channel
    #   get number of times channels is recommended: target = channel
    #   normalize by number of videos with recommendations, or source = channel






    # ----
