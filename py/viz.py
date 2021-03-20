'''
Multiple visualization of the data
- video_volume_timeline: number of videos published per day over a period
'''

from .job import *
from .model import *

from py import *
import pandas as pd
import numpy as np
import datetime

import matplotlib.pyplot as plt
import seaborn  as sns
pd.options.display.max_columns = None

def video_volume_timeline_data(start_date, end_date):
    sql = f'''
        select count(v.id) as n, v.pubdate
        from video v
        join pipeline p on p.video_id = v.video_id
        where p.status = 'active'
        and v.pubdate > '{start_date}'
        and  v.pubdate < '{end_date}'
        group by pubdate
    '''
    print(sql)
    df = pd.read_sql(sql, job.db.conn)
    return df

def video_volume_timeline_viz(df,start_date, end_date):
    wdf = df.groupby(by = 'w').agg({'n': mean, 'pubdate': min}).reset_index()

    fig = plt.figure(figsize= (12,6))
    plt.grid(alpha  = 0.3)
    sns.barplot(x = 'pubdate', y = 'n', data = wdf)
    plt.hlines(wdf.n.mean(), 0, wdf.shape()[0])
    plt.title(f"Number of French videos on Youtube between  {start_date} and  {end_date}")
    plt.ylabel("Number of videos")
    plt.xlabel("")
    plt.xticks(rotation=45)
    plt.annotate("avg: 14.3k", (-1, 14500))
    sns.despine()
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':

    start_date = '2020-08-31'
    end_date = '2021-01-01'
    df = video_volume_timeline_data(start_date, end_date)







# --------
