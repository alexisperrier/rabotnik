
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

    ld = LangDetector()
    if True:

        sql = '''
            select ch.channel_id,
                p.lang, p.lang_conf, ch.title, ch.description
            from channel ch
            join pipeline p on p.channel_id = ch.channel_id
            where (ch.country is null or ch.country = '')
            and p.lang_conf is null
            and p.status = 'foreign'
            and ch.description != ''
            order by ch.activity_score desc
        '''
        df = pd.read_sql(sql, job.db.conn)

        df['lang_predicted'] = df.apply(lambda d : ld.predict(  ' '.join([d.description,d.title]).replace("\n",' ')) , axis = 1)
        df['lang_conf']      = df.lang_predicted.apply(lambda d : d['conf'])
        df['lang']           = df.lang_predicted.apply(lambda d : d['lang'])

        wk = df[df.lang_conf <= 0.7].reset_index(drop = True).copy()

        st = df[df.lang_conf > 0.7].reset_index(drop = True).copy()
        k = 0
        for i, d in st.iterrows():
            sql = f'''
                update pipeline
                set lang = '{d.lang}',
                lang_conf = {d.lang_conf}
                where channel_id = '{d.channel_id}'
            '''
            job.execute(sql)
            print(f" {k}/{st.shape[0]} [{d.channel_id}] {job.db.cur.rowcount} \t {d.lang} {np.round(d.lang_conf,2)} {d.title}")
            k +=1

    if True:
        sql = '''
            select ch.channel_id,
                p.lang, p.lang_conf, ch.title, ch.description
            from channel ch
            join pipeline p on p.channel_id = ch.channel_id
            where (ch.country is null or ch.country = '')
            and (p.lang_conf is null or p.lang = '--' or p.lang_conf <= 0.2)
            and p.status = 'active'
            order by ch.activity_score desc
            limit 5000
        '''

        df = pd.read_sql(sql, job.db.conn)


        for i,d in df.iterrows():
            sql = f'''
                select summary || ' ' || title as text from video where channel_id = '{d.channel_id}'
                order by id desc limit 10
            '''
            tt = pd.read_sql(sql, job.db.conn)
            if not tt.empty:
                df.loc[i, 'video_text'] = ' '.join( tt.text.values)
            else:
                # print(f"{d.channel_id} no vids no text")
                df.loc[i, 'video_text'] = ''

        print("-- done loading video text")
        df.loc[df['video_text'].isna(), 'video_text'] = ''
        df.loc[df['description'].isna(), 'description'] = ''
        df.loc[df['title'].isna(), 'title'] = ''


        df['lang_predicted'] = df.apply(lambda d : ld.predict(  ' '.join([d.video_text.lower(), d.description.lower(),d.title.lower()]).replace("\n",' ')) , axis = 1)
        df['lang_conf']      = df.lang_predicted.apply(lambda d : d['conf'])
        df['lang']           = df.lang_predicted.apply(lambda d : d['lang'])
        print("-- done predicting lang")

        if True:
            k = 0
            for i, d in df.iterrows():
                sql = f'''
                    update pipeline
                    set lang = '{d.lang}',
                    lang_conf = {d.lang_conf}
                    where channel_id = '{d.channel_id}'
                '''
                job.execute(sql)
                print(f" {k}/{df.shape[0]} [{d.channel_id}] {job.db.cur.rowcount} \t {d.lang} {np.round(d.lang_conf,2)} {d.title}")
                k +=1


    # flowname  = 'video_scrape'
    # classname = 'Flow'+ ''.join(word.title() for word in flowname.split('_'))
    # klass = globals()[classname]

    # op = klass(flowtag = True, mode = 'local', counting = True)
    # for operation in op.operations:
    #     start_time = datetime.datetime.now()
    #     print("--",operation)
    #     if op.ok:
    #         getattr(op, operation)()
    #     else:
    #         print("nok", op.reason,op.status_code)
    #         break;
    #     delta_time = (datetime.datetime.now() - start_time).seconds
    #     print("--",operation,f"execution time {delta_time}s")
    #
    # op.execution_time()
    #




# ----
