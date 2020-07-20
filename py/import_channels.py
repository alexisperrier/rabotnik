import numpy as np
import pandas as pd
import os
import re
import json
import datetime
from tqdm import tqdm
from py import *

if __name__ == '__main__':


    filepath    = './data/import/Emma_Gauthier_20200720_Les_Internettes.csv'
    filename    = filepath.split('/')[-1]
    origin      = 'Internettes'
    if False:
        '''
            Read input file, handle field names and check channel ids validity
        '''
        # read input file
        data = pd.read_csv(filepath)
        data['channel_id'] = data['Lien de la chaîne'].apply(lambda d : d.split('/')[-1])

        # check channel validity (24)
        data['valid'] = data.channel_id.apply(lambda id : len(id) == 24)
        print(f" {data.shape[0]} / {data[data.valid].shape[0]} valid/ total channels ")

        channel_ids = data[data.valid].channel_id.values

    if False:
        '''
        Check how many channels already exist
        '''
        sql = f'''
            select ch.channel_id, p.status, ch.title, ch.description, ch.activity
            from channel ch
            join pipeline p on p.channel_id = ch.channel_id
            where ch.channel_id in ('{"','".join(channel_ids)}')
        '''
        df = pd.read_sql(sql, job.db.conn)
        existing_channel_ids = df.channel_id.values

        print(f"{df.shape[0]} channels found  / {data.shape[0]} total")

    if False:
        '''
            add channels to origin table
            create channels that don't exist yet
        '''
        # add channels to origin
        n_origin, n_created_pipelines, n_created_channels   = 0, 0 , 0
        for i,d in tqdm(data.iterrows()):
            sql = f'''
                 insert into origin
                 (channel_id, origin, filename, created_at)
                 values
                 ('{d.channel_id}', '{origin}', '{filename}', now())
                 on conflict (channel_id, origin ) DO NOTHING;
            '''
            job.execute(sql)
            n_origin += job.db.cur.rowcount

            n_created_channels  += Channel.create(d.channel_id, '{origin}')
            n_created_pipelines +=Pipeline.create(idname = 'channel_id',item_id = d.channel_id)

        print(f"{n_origin} channels added to origin")
        print(f"{n_created_channels} new channels \t {n_created_pipelines} created pipelines")



    if True:
        '''
            make all channels incomplete to reset stats
            set country and lang to FR
            force rss feed parsing
        '''

        # set status to incomplete and lang to 'fr' for all channels
        sql = f'''
            update pipeline set status = 'incomplete', lang = 'fr'
            where channel_id in ('{"','".join(channel_ids)}')
        '''
        job.execute(sql)


        # force rss and set country
        sql = f'''
            update channel set country = 'FR', rss_next_parsing = now() - interval '1 month'
            where channel_id in ('{"','".join(channel_ids)}')
        '''
        job.execute(sql)


        # check missing channels are all in next complete_channels
        klass = globals()['FlowCompleteChannels']
        params = {'flowtag' : False, 'mode' : 'dbquery', 'counting' : True, 'max_items': 50}
        op = klass(**params)
        op.get_items()

        # queued channel_ids
        queued_channel_ids  = op.data.channel_ids.values
        missing_channel_ids = set(channel_ids).intersection(set(existing_channel_ids))

        check =  all(id in missing_channel_ids  for id in queued_channel_ids)
        if check:
            print("all missing_channel_ids are set for completion")
        else:
            print("these channels should be set for completion but are not")

        # check all channels are all in feed parsing
        # TODO





# --------
