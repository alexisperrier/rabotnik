'''
Given a set of videos, extract  all the related recommendations records and dump into csv
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
    data_path = "/Users/alexis/amcp/UGE/rabotnik/data/cncdh_2020_video_id_0103.csv"
    df = pd.read_csv(data_path)

    video_ids = df.video_id.values
    print(len(video_ids))
    video_ids = [id for id in video_ids if len(id) == 11]

    start_ = 0
    delta = 200
    data = []
    while start_< len(video_ids) :
    # while start_< 1000 :
        end_ = min(start_ + delta, len(video_ids))
        # print(start_, end_)
        ids = "','".join(video_ids[start_:end_])
        start_ += delta

        sql = f'''
            select src_video_id, tgt_video_id, tgt_video_harvested_at
            from video_recommendations
            where src_video_id in ('{ids}')
            or tgt_video_id in ('{ids}')
        '''
        job.execute(sql)
        print(f"- {start_}, {end_} {job.db.cur.rowcount} rows")
        for r in  job.db.cur.fetchall():
            data.append({
                'src_video_id': r[0],
                'tgt_video_id': r[1],
                'tgt_video_harvested_at': r[2]
            })

    data = pd.DataFrame(data)
    data.to_csv('./data/video_recommendations_20200320.1.0.csv', index = False)




# --
