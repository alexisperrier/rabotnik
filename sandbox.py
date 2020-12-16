
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

    flowname  = 'video_comments'
    classname = 'Flow'+ ''.join(word.title() for word in flowname.split('_'))
    klass = globals()[classname]
    job.config['offset_factor'] = 0

    params = {'flowtag' : False, 'mode' : 'local', 'counting' : True, 'max_items': 5}
    op = klass(**params)
    op.get_items()
    # # op.freeze()
    # # op.query_api()
    # # op.decode()
    # # op.ingest()
    # # op.postop()
    #
    #
    # for operation in op.operations:
    #     start_time = datetime.datetime.now()
    #     print("== --",operation)
    #     if op.ok:
    #         getattr(op, operation)()
    #     else:
    #         print("nok", getattr(op, 'reason', ''), getattr(op, 'status_code', ''))
    #         break;
    #     delta_time = (datetime.datetime.now() - start_time).seconds
    #     print("--",operation,f"execution time {delta_time}s")

    op.execution_time()

# ------------
    if False:
        sql = f'''
        select
            ch.channel_id,
            ch.title as channel_title,
            ch.created_at as channel_created_at,
            ch.retrieved_at as channel_infos_retrieved_at,
            p.status,
            cs.views as channel_views,
            cs.subscribers as channel_subscribers_count,
            cs.videos as channel_videos_count,
            (select string_agg(col2.title, ', ')  from collections col2
                join collection_items ci2 on col2.id = ci2.collection_id
                where ci2.collection_id in (13,15,20) and ci2.channel_id = ch.channel_id
            ) as collections,
            cs.retrieved_at as channel_stats_retrieved_at
        from channel ch
        join pipeline p on ch.channel_id = p.channel_id
        left join channel_stat cs on ch.channel_id = cs.channel_id
        join collection_items ci on ci.channel_id = ch.channel_id
        where ci.collection_id in (13,15,20)
        order by channel_title;'''

        dfch = pd.read_sql(sql, job.db.conn)

        dfch = dfch.drop_duplicates(subset = ['channel_id']).reset_index(drop = True)
        dfch.to_csv('./data/export/export_channels_20200915.csv', index = False)

        from tqdm import tqdm
        res = pd.DataFrame()
        res = {}
        for channel_id in tqdm(dfch.channel_id.unique()):

            sql = f'''
                select max(vs.like_count), vs.video_id,  v.channel_id
                from video_stat vs
                join video v on v.video_id = vs.video_id
                where vs.like_count is not null
                and v.channel_id = '{channel_id}'
                group by vs.video_id,  v.channel_id
            '''
            rdf = pd.read_sql(sql , job.db.conn)
            res = pd.concat([res, rdf])

        res.columns = ['likes', 'video_id', 'channel_id']
        res.to_csv('./data/export/export_likes_raw_20200915.csv', index = False)
        c = res[['likes','channel_id']].groupby(by = 'channel_id').count().reset_index()
        c.columns = ['channel_id', 'likes_count']
        s = res[['likes','channel_id']].groupby(by = 'channel_id').sum().reset_index()
        s.columns = ['channel_id','likes_sum']
        dflk = pd.merge(s,c, on = 'channel_id')
        dflk['likes_avg'] = dflk.likes_sum / dflk.likes_count
        dflk.columns = ['channel_id', 'likes_sum', 'likes_video_count', 'likes_avg']
        dflk.to_csv('./data/export/export_likes_avg_20200915.csv', index = False)

        # sql = f'''
        #     select max(vs.like_count), vs.video_id,  ch.channel_id
        #     from video_stat vs
        #     join video v on v.video_id = vs.video_id
        #     join channel ch on v.channel_id = ch.channel_id
        #     join collection_items ci on ci.channel_id = ch.channel_id
        #     where vs.like_count is not null
        #     and ci.collection_id in (13,15,20)
        #     group by vs.video_id,  ch.channel_id
        # '''
        #
        # dflk = pd.read_sql(sql, job.db.conn)

        # sql = f'''select count(tgt_video_id) as indegree, ch.channel_id
        # from video_recommendations vr
        # join video v on v.video_id = vr.tgt_video_id
        # join channel ch on ch.channel_id = v.channel_id
        # join collection_items ci on ci.channel_id = ch.channel_id
        # where ci.collection_id in (13,15,20)
        # group by ch.channel_id ;'''
        #
        # dfin = pd.read_sql(sql, job.db.conn)


        sql = f'''select v.channel_id, vr.tgt_video_id, vr.tgt_video_harvested_at
        from video_recommendations vr
        join video v on v.video_id = vr.tgt_video_id
        where v.channel_id in (
            select distinct ci.channel_id from collection_items ci where ci.collection_id in (13,15,20)
        );'''
        dfreco = pd.read_sql(sql, job.db.conn)
        dfreco.to_csv('./data/export/upstream_reco_export_20200915.csv', index = False)

        indg = dfreco[['channel_id', 'tgt_video_id']].groupby(by = 'channel_id').count().reset_index()
        indg.columns = ['channel_id', 'indegree']
        # indg.reset_index(drop = True, inplace = True)
        indg.to_csv('./data/export/export_indegree_20200915.csv', index = False)

        data = pd.merge(dfch, indg, on = 'channel_id', how = 'outer')
        data = pd.merge(data, dflk, on = 'channel_id', how = 'outer')

        data.to_csv('./data/export/export_medialab_gj_sig_20200915.csv', index = False)





    # ----
