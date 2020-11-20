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
import csv
from tqdm import tqdm

from pathlib import Path

if __name__ == '__main__':
    collection_id = 21
    EXPORT = False
    export_tag  = '10pct_20201007'
    export_path = './data/export/'


    # ------------------------------------------------------------------------
    # export channels Part I
    # ------------------------------------------------------------------------
    sql = f'''
        select ch.channel_id, ch.title, ch.description, ch.country, ch.custom_url,
        ch.created_at, ch.origin, og.origin, ch.has_related, ch.thumbnail,
        ch.activity_score, ch.activity, p.lang, p.lang_conf, p.status,
        cs.views, cs.subscribers, cs.videos, cs.retrieved_at as stats_retrieved_at
        from channel ch
        left join channel_stat cs on cs.channel_id = ch.channel_id
        left join origin og on og.channel_id = ch.channel_id
        left join pipeline p on p.channel_id = ch.channel_id
        join collection_items ci on ci.channel_id = ch.channel_id
        where ci.collection_id = {collection_id}
    '''
    channels = pd.read_sql(sql, job.db.conn)
    # channels = channels.loc[:,~channels.columns.duplicated()]
    channels = channels.sort_values(by = 'title').reset_index(drop = True)
    for col in ['views', 'subscribers','videos']:
        channels.loc[channels[col].isna(),col] = -1
        channels[col] = channels[col].astype(int)
    print(f"{channels.shape[0]} channels")



    # ------------------------------------------------------------------------
    # export videos
    # ------------------------------------------------------------------------

    sql = f'''
        select v.video_id, v.channel_id, ch.title, pch.status as channel_status, v.pubdate,
            v.retrieved_at, v.origin, p.status,
            v.seconds, v.duration, v.title, v.summary
        from video v
        join pipeline p on p.video_id = v.video_id
        join channel ch on v.channel_id = ch.channel_id
        join pipeline pch on pch.channel_id = v.channel_id
        where v.channel_id in ('{"','".join(channels.channel_id.values)}')
        order by v.channel_id, v.published_at desc
    '''
    videos = pd.read_sql(sql, job.db.conn)
    videos = videos.loc[:,~videos.columns.duplicated()]

    print(f"{videos.shape[0]} videos")

    # ------------------------------------------------------------------------
    # channels Part II
    # ------------------------------------------------------------------------

    # aggregated likes and ...  and
    video_ids = videos.video_id.unique()
    start = 0
    step = 1000
    res = pd.DataFrame()
    while start < len(video_ids):
        sliced_video_ids = video_ids[start:start+step]
        sql = f'''
            select max(vs.like_count) as likes, vs.video_id,  v.channel_id
            from video_stat vs
            join video v on v.video_id = vs.video_id
            where vs.like_count is not null
            and vs.video_id in  ('{"','".join(sliced_video_ids)}')
            group by vs.video_id,  v.channel_id
        '''
        print('-', end = '')
        start += step
        tmp = pd.read_sql(sql , job.db.conn)
        res = pd.concat([res, tmp])

    chlikes = res

    c = chlikes[['likes','channel_id']].groupby(by = 'channel_id').count().reset_index()
    c.columns = ['channel_id', 'likes_count']
    s = chlikes[['likes','channel_id']].groupby(by = 'channel_id').sum().reset_index()
    s.columns = ['channel_id','likes_sum']

    dflk = pd.merge(s,c, on = 'channel_id')
    dflk['likes_avg'] = dflk.likes_sum / dflk.likes_count
    dflk.columns = ['channel_id', 'likes_sum', 'likes_video_count', 'likes_avg']

    channels = pd.merge(channels, dflk, on = 'channel_id', how = 'outer' )

    # ------------------------------------------------------------------------
    #  indegree
    # ------------------------------------------------------------------------

    sql = f'''select v.channel_id, vr.tgt_video_id, vr.tgt_video_harvested_at
        from video_recommendations vr
        join video v on v.video_id = vr.tgt_video_id
        where v.channel_id in (
            select distinct ci.channel_id from collection_items ci where ci.collection_id in (21)
    )'''

    dfreco = pd.read_sql(sql, job.db.conn)

    indg = dfreco[['channel_id', 'tgt_video_id']].groupby(by = 'channel_id').count().reset_index()
    indg.columns = ['channel_id', 'indegree']

    channels = pd.merge(channels, indg, on = 'channel_id', how = 'outer' )


    # ------------------------------------------------------------------------
    #  recommendations
    # ------------------------------------------------------------------------

    video_ids = videos.video_id.unique()
    start = 0
    step = 100
    res = pd.DataFrame()
    while start < len(video_ids):
        sliced_video_ids = video_ids[start:start+step]

        sql = f'''
                select vr.src_video_id, vr.tgt_video_id, vr.harvest_date,
                    srcv.channel_id as scr_channel_id, srcch.title as scr_channel_title,
                    tgtv.channel_id as tgt_channel_id, tgtch.title as tgt_channel_title
                from video_recommendations vr
                join video srcv on srcv.video_id = vr.src_video_id
                join channel srcch on srcv.channel_id = srcch.channel_id
                join video tgtv on tgtv.video_id = vr.tgt_video_id
                join channel tgtch on tgtv.channel_id = tgtch.channel_id
                where vr.src_video_id in ('{"','".join(sliced_video_ids)}')
            UNION
                select vr.src_video_id, vr.tgt_video_id, vr.harvest_date,
                    srcv.channel_id as scr_channel_id, srcch.title as scr_channel_title,
                    tgtv.channel_id as tgt_channel_id, tgtch.title as tgt_channel_title
                from video_recommendations vr
                join video srcv on srcv.video_id = vr.src_video_id
                join channel srcch on srcv.channel_id = srcch.channel_id
                join video tgtv on tgtv.video_id = vr.tgt_video_id
                join channel tgtch on tgtv.channel_id = tgtch.channel_id
                where vr.tgt_video_id in ('{"','".join(sliced_video_ids)}')
        '''


        print(f"{start}", end = '| ')
        start += step
        tmp = pd.read_sql(sql , job.db.conn)
        res = pd.concat([res, tmp])

    recos = res

    # ----------------------------------------------------------------------
    #  related channels
    # ----------------------------------------------------------------------

    sql = f'''
        select rc.channel_id as src_channel_id,rc.related_id as tgt_channel_id,
        ch1.title as src_channel_title,
        ch2.title as tgt_channel_title
        from related_channels rc
        join channel ch1  on ch1.channel_id = rc.channel_id
        join channel ch2  on ch2.channel_id = rc.related_id
        where rc.channel_id in ('{"','".join(channels.channel_id.values)}')
    '''

    related = pd.read_sql(sql , job.db.conn)

    if EXPORT:
        channels.to_csv(f"{export_path}channels_{export_tag}.csv", quoting = csv.QUOTE_ALL, index = False)

        videos.to_csv(f"{export_path}videos_{export_tag}.csv", quoting = csv.QUOTE_ALL, index = False)

        recos.to_csv(f"{export_path}recos_{export_tag}.csv", quoting = csv.QUOTE_ALL, index = False)
        related.to_csv(f"{export_path}related_{export_tag}.csv", quoting = csv.QUOTE_ALL, index = False)


Dealing with bureaucracy is good for your karma
The only way to win is to learn to accept defeat







# =======
