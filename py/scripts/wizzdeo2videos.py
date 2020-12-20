'''
2020 12 17
fichier wizzdeo
1400+ chaines
par chaines (1111.json) liste des videos

- parcourrir les fichiers chaines
- extraire les videos
- check videos exist
- creer fichier videos manquantes
'''

import numpy as np
import pandas as pd
import os, re, json, csv, sys
import datetime, time
from tqdm import tqdm
import glob
import subprocess
import datetime

from py import *

if __name__ == "__main__":

    # get all files from data folder
    # DATAPATH = "./data/videos/videos/"
    DATAPATH = "./data/UPEM_2019_06_01_2020_12_12/Decembre_2020/data/videos/"
    files = sorted([f for f in glob.glob(f"{DATAPATH}*.json")])


    empty_channel_count = []
    total_videos_created = 0
    total_videos_wizzdeo = 0
    start = 0
    number_of_files = 500
    big_files = []
    k = start
    for file in files[start:]:
        start_time = datetime.datetime.now()
        with open(file) as f:
            data = json.load(f)
        if len(data) == 0:
            empty_channel_count.append(file)
        # elif len(data) > 2000:
        #     big_files.append(file)
        #     print(f"big file {file} -- skipping")
        #     continue
        else:
            # video_ids = [d['yt_id'] for d in data if d['uploaded'][:4] == '2020'   ]
            videos = pd.DataFrame(
                [(d['yt_id'],d['uploaded'][:4]) for id,d in data.items() ],
                columns = ['video_id', 'year'])
            videos['year'] = videos.year.astype('int')
            video_ids = videos[videos.year == 2020].video_id.values
            created_videos_count = 0
            if (len(video_ids) > 5000):
                big_files.append(file)
                print(f"big file {file} --  {len(video_ids)} videos")
            #     continue
            # # elif ((len(video_ids) > 1000)):
                total_videos_wizzdeo += len(video_ids)
                # get missing videos
                sql = f'''
                    select video_id
                    from video
                    where video_id in ('{"','".join(video_ids)}')
                '''
                job.execute(sql)
                known_video_ids = [r[0] for r in  job.db.cur.fetchall()]
                missing_video_ids = [id for id in video_ids if id not in known_video_ids]
                print(f"== {file} \t {len(video_ids)} videos {len(missing_video_ids)} missing_video_ids")

                # create missing videos
                for video_id in tqdm(missing_video_ids):
                    created_videos_count += Video.create_from_id(video_id, "wizzdeo")
                    Pipeline.create(idname = 'video_id',item_id = video_id)

                total_videos_created += created_videos_count
            k +=1
            if k%100 == 0:
                print("--" * 20)
                print(f"========  total_videos_created : {total_videos_created} / {total_videos_wizzdeo} ratio: {np.round(100.0 *total_videos_created / total_videos_wizzdeo,4)}%")
            print(f"({k}/{len(files)})  {created_videos_count}/{len(video_ids)} new videos in {(datetime.datetime.now() - start_time).seconds}s")

    print(f"======== \n  total_videos_created : {total_videos_created} / {total_videos_wizzdeo} ratio: {np.round(100.0 *total_videos_created / total_videos_wizzdeo,4)}%")

    # df = pd.DataFrame(video_ids, columns = ['video_id'])
    # df.to_csv("./data/videos/wizzdeo_video.csv")

    '''
    check if video in db
    '''
    # print("")
    # offset = 100
    # start = 0
    # total_iterations = int(len(video_ids) / offset) +1
    # k = 0
    # created_videos_count = 0
    # while start  < len(video_ids) + offset:
    #     vids = video_ids[start:start + offset]
    #     sql = f'''
    #         select video_id
    #         from video
    #         where video_id in ('{"','".join(vids)}')
    #     '''
    #     job.execute(sql)
    #     known_video_ids = [r[0] for r in  job.db.cur.fetchall()]
    #     vids = [id for id in vids if id not in known_video_ids]
    #     # creating videos
    #     n = 0
    #     for video_id in vids:
    #         n += Video.create_from_id(video_id, "wizzdeo")
    #         Pipeline.create(idname = 'video_id',item_id = video_id)
    #
    #     created_videos_count  += n
    #
    #     k +=1
    #     start += offset
    #     if k%100 == 0:
    #         print(f"({k}/{total_iterations}) \t  {created_videos_count} videos created")










# ------
