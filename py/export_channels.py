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
import isodate

if __name__ == '__main__':

    EXPORT = True

    origin      = 'Internettes'
    export_tag  = 'internettes_20200722'
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
    channels = channels.sort_values(by = 'status').reset_index(drop = True)
    print(f"{channels.shape[0]} channels")
    if EXPORT:
        channels.to_csv(f"{export_path}channels_{export_tag}.csv", quoting = csv.QUOTE_ALL, index = False)

    # videos
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

    if False:
        '''
            if the channels of the videos are foreign the videos won't be completed
            need to disable care crontab
            and set the channel status to active
        '''
        videos.groupby(by = ['status','channel_status']).count().reset_index()
        sql = f'''
            update pipeline set status = 'active'
            where channel_id in ('{"','".join(videos[(videos.status == 'incomplete') & (videos.channel_status == 'foreign')].channel_id.unique())}')
            and status = 'foreign'
        '''
        job.execute(sql)

    if EXPORT:
        videos.to_csv(f"{export_path}videos_{export_tag}.csv", quoting = csv.QUOTE_ALL, index = False)

    # recommendations
    sql = f'''
            select vr.src_video_id, vr.tgt_video_id, vr.harvest_date,
                srcv.channel_id as scr_channel_id, srcch.title as scr_channel_title,
                tgtv.channel_id as tgt_channel_id, tgtch.title as tgt_channel_title
            from video_recommendations vr
            join video srcv on srcv.video_id = vr.src_video_id
            join channel srcch on srcv.channel_id = srcch.channel_id
            join video tgtv on tgtv.video_id = vr.tgt_video_id
            join channel tgtch on tgtv.channel_id = tgtch.channel_id
            where vr.src_video_id in ('{"','".join(videos.video_id.values)}')
        UNION
            select vr.src_video_id, vr.tgt_video_id, vr.harvest_date,
                srcv.channel_id as scr_channel_id, srcch.title as scr_channel_title,
                tgtv.channel_id as tgt_channel_id, tgtch.title as tgt_channel_title
            from video_recommendations vr
            join video srcv on srcv.video_id = vr.src_video_id
            join channel srcch on srcv.channel_id = srcch.channel_id
            join video tgtv on tgtv.video_id = vr.tgt_video_id
            join channel tgtch on tgtv.channel_id = tgtch.channel_id
            where vr.tgt_video_id in ('{"','".join(videos.video_id.values)}')
    '''

    recos = pd.read_sql(sql, job.db.conn)
    print(f"{recos.shape[0]} recommendations")
    if EXPORT:
        recos.to_csv(f"{export_path}recos_{export_tag}.csv", quoting = csv.QUOTE_ALL, index = False)




# --------------
