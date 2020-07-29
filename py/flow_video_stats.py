from .flow import *
import datetime

class FlowVideoStats(Flow):

    varnames_api2db = {
        'id': 'video_id',
        'statistics.viewCount': "views"
    }

    def __init__(self,**kwargs):
        self.flowname = 'video_stats'
        super().__init__(**kwargs)
        self.endpoint   = 'videos'
        self.idname     = 'video_id'
        self.parts      = 'statistics'
        self.fields     = 'items(id,statistics(viewCount))'

    def tune_sql(self):
        timespan_01 = (datetime.datetime.now() - datetime.timedelta(days = 1)).strftime('%Y-%m-%d')
        timespan_02 = "','".join( [(datetime.datetime.now() - datetime.timedelta(days = d)).strftime('%Y-%m-%d') for d in [1,2,3,4,5,6,7,14,21,28,60]])
        self.sql = self.sql.replace('{timespan_01}', timespan_01).replace( '{timespan_02}', timespan_02)

    def code_sql(self):
        '''
        No gaming videos
        Channel must be active (not foreign)
        '''
        return '''
             select v.video_id
             from video v
             join pipeline p on p.video_id = v.video_id
             join pipeline pch on p.channel_id = v.channel_id
             left join flow as fl on fl.video_id = v.video_id and fl.flowname = 'video_stats'
             left join video_stat vs on ( (vs.video_id = v.video_id) and (vs.viewed_at > '{timespan_01}'))
             where v.pubdate in ('{timespan_02}')
                and pch.status = 'active'
                and v.category_id != 20
                and fl.id is null
                and vs.id is null
                and p.status = 'active'
         '''

    def decode(self):
        super().decode()
        self.df['source']    = 'api'
        self.df['viewed_at'] = datetime.datetime.now().strftime('%Y-%m-%d')

    def ingest(self):
        print(f"== {self.df.shape} to insert")
        for i,d in self.df.iterrows():
            VideoStat.create(d)
            # self.release(d.video_id)







# -----------------
