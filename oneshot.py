'''

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

    # flowname  = 'video_stats'
    # classname = 'Flow'+ ''.join(word.title() for word in flowname.split('_'))
    # klass = globals()[classname]
    #
    # params = {'flowtag' : True, 'mode' : 'local', 'counting' : False, 'max_items': 50}
    # op = klass(**params)

    # read all data/captions folders
    HTML_TAG_REGEX = re.compile(r'<[^>]*>', re.IGNORECASE)

    caption_path = './data/captions/'
    files = sorted([filename for filename in glob.glob(f"{caption_path}videos_no_caption_batch_*.csv")])
    filename = files[12]
    df = pd.read_csv(filename)
    # data = df[df.found > 0].copy()
    # data.reset_index(inplace = True, drop = True)
    n_captions = 0
    channel_ids = df[df.found > 0].channel_id.unique()
    k = 0
    for channel_id in channel_ids:
        k +=1
        channel_path = f"./data/captions/{channel_id}"
        caption_files = sorted([filename for filename in glob.glob(f"{channel_path}/*.*")])
        print("=="*20)
        print(f"[{channel_id}] {k}/{len(channel_ids)} {len(caption_files)} files")
        for capfile in caption_files:
            with open(capfile) as fp:
                text = [line.replace('\n','').strip() for line in fp.readlines()]

            text = [re.sub(HTML_TAG_REGEX,'',t) for t in text if (not re.match( '^[0-9].*', t)) & (len(t) >0)]
            text = [t for t in text if t not in ['WEBVTT','Kind: captions','Language: fr']]
            captions = pd.DataFrame(text, columns = ['text']).drop_duplicates().text.values
            video_id = capfile.split('/')[-1].split('.')[0]
            if len(captions) > 0:
                print(video_id,len(' '.join(captions).split()),'\t',captions[0])

                sql = f'''
                    insert into caption (video_id, status, caption, wordcount, processed_at, caption_type)
                    values ('{video_id}',
                        'acquired',
                        $${TextUtils.to_db(' '.join(captions))}$$,
                        {len(' '.join(captions).split())},
                        now() ,
                        'youtube-dl'
                    )
                    ON CONFLICT (video_id)  DO
                    UPDATE SET
                        status = 'acquired',
                        caption = $${TextUtils.to_db(' '.join(captions))}$$,
                        wordcount = {len(' '.join(captions).split())},
                        caption_type = 'youtube-dl'
                '''
                job.execute(sql)
                res_count = job.db.cur.rowcount
                if res_count == 0:
                    print("***" * 20)
                    print(f"[{video_id}] \n{sql}  ")
                    print("***" * 20)
                else:
                    n_captions += res_count
                    # print(f"-- caption for {video_id} ")

                cond = (df.channel_id == channel_id) & (df.video_id == video_id)
                df.loc[cond,'sql'] = res_count
                df.to_csv(filename, index = False, quoting = csv.QUOTE_ALL)

        print("== n_captions",n_captions)


# select c.video_id from caption c
# join video v on v.video_id = c.video_id
# where v.channel_id = 'UC03qCsERk3cQPmhdI0SI6xQ';
#
#  u0oDA31yQYg
#  cKiUihKcZ18
#  -CvsKp_KzUU




    # ----
