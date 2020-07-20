'''
Given an origin, export
all channels, and videos
for all videos export all related videos

'''
import numpy as np
import pandas as pd
import os
import re
import json
import csv
import datetime
from tqdm import tqdm
from py import *

if __name__ == '__main__':


    origin      = 'Internettes'
    export_tag  = 'internettes_20200720'
    export_path = './data/export/'

    sql = f'''
        select ch.*, p.*, cs.*
        from channel ch
        join channel_stat cs on cs.channel_id = ch.channel_id
        join origin og on og.channel_id = ch.channel_id
        join pipeline p on p.channel_id = ch.channel_id
        where og.origin = '{origin}'
    '''
    channels = pd.read_sql(sql, job.db.conn)
    channels = channels.loc[:,~channels.columns.duplicated()]
    print(f"{channels.shape[0]} channels")
    channels.to_csv(f"{export_path}channels_{export_tag}.csv", quoting = csv.QUOTE_ALL, index = False)

    # videos
    sql = f'''
        select v.video_id, v.channel_id, v.pubdate, v.retrieved_at, v.origin, v.seconds, v.title, v.summary
        from video v
        where v.channel_id in ('{"','".join(channels.channel_id.values)}')
        order by v.channel_id, v.published_at desc
    '''
    videos = pd.read_sql(sql, job.db.conn)
    videos = videos.loc[:,~videos.columns.duplicated()]
    print(f"{videos.shape[0]} videos")
    videos.to_csv(f"{export_path}videos_{export_tag}.csv", quoting = csv.QUOTE_ALL, index = False)

    # recommendations
    sql = f'''
        select vr.src_video_id, vr.tgt_video_id, vr.harvest_date, srcv.channel_id as scr_channel_id, tgtv.channel_id as tgt_channel_id
        from video_recommendations vr
        join video srcv on srcv.video_id = vr.src_video_id
        join video tgtv on tgtv.video_id = vr.tgt_video_id
        where vr.src_video_id in ('{"','".join(videos.video_id.values)}')
        UNION
        select vr.src_video_id, vr.tgt_video_id, vr.harvest_date, srcv.channel_id as scr_channel_id, tgtv.channel_id as tgt_channel_id
        from video_recommendations vr
        join video srcv on srcv.video_id = vr.src_video_id
        join video tgtv on tgtv.video_id = vr.tgt_video_id
        where vr.tgt_video_id in ('{"','".join(videos.video_id.values)}')
    '''

    recos = pd.read_sql(sql, job.db.conn)
    print(f"{recos.shape[0]} recommendations")
    recos.to_csv(f"{export_path}recos_{export_tag}.csv", quoting = csv.QUOTE_ALL, index = False)




# --------------
