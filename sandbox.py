
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

    # version complete_channel (no videos yet)

    sql = '''
        select ch.channel_id, ch.country, pp.lang, pp.lang_conf, ch.title, ch.description
            from channel ch
            join pipeline pp on pp.channel_id = ch.channel_id
            left join border b on b.channel_id = ch.channel_id
            where (ch.country is null or ch.country = '')
                and b.id is null
                and pp.lang !='fr'
                and pp.lang_conf > 0.2
    '''
    df = pd.read_sql(sql, job.db.conn)

    if False:
        ld = LangDetector()
        sql = '''
            select ch.channel_id, ch.country, ch.description, ch.title, pp.activity_score, pp.status, pp.lang
            from channel ch
            join pipeline pp on pp.channel_id = ch.channel_id
            where ch.country = 'FR'
            and pp.lang != 'fr'
            order by ch.id desc
        '''
        df = pd.read_sql(sql, job.db.conn)
        df['lang_predicted'] = df.apply(lambda d : ld.predict(  ' '.join([d.title,d.description]).replace("\n",' ')) , axis = 1)
        df['lang_conf'] = df.lang_predicted.apply(lambda d : d['conf'])
        df['lang_predicted'] = df.lang_predicted.apply(lambda d : d['lang'])

        print(df[df.lang != df.lang_predicted].shape)
        df = df[df.lang != df.lang_predicted].reset_index(drop = True)
        k = 1000
        for i,d in df[1000:].iterrows():
            k += 1
            n = Pipeline.update_lang(idname = 'channel_id',  item_id = d.channel_id, lang = d.lang_predicted, lang_conf = d.lang_conf)
            print(f"\n[{k}] {d.channel_id} {d.lang} -> {d.lang_predicted} ({d.lang_conf}) \t {n} \n\t[{d.title}] {d.description[:90]}")

    # job.execute(sql)
    # data = []
    # for res in tqdm(job.db.cur.fetchall()):
    #     # print()
    #     # print("=="*20)
    #     channel_id = res[0]
    #     text = ' '.join([res[1],res[2]])
    #     wordcount = len(text.split())
    #     if wordcount > 2:
    #         ld.predict(text.replace("\n",' '))
    #         data.append({'channel_id': channel_id, 'lang': ld.lang, 'conf':ld.conf, 'text': text, 'score': res[3], 'status':res[4]})
    #     else:
    #         data.append({'channel_id': channel_id, 'lang': None, 'conf':None, 'text': text, 'score': res[3], 'status':res[4]})
    #     # print(f"{channel_id}, lang {ld} \n{text[:100]} ")
    # df = pd.DataFrame(data)
    #
    # for i,d in df[~df.conf.isna()].iterrows():
    #     sql = f" update pipeline set lang = '{d.lang}', lang_conf = {d.conf} where channel_id = '{d.channel_id}' "
    #     job.execute(sql)

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
