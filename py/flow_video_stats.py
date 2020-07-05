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
        # self.max_items  = 50
        self.endpoint   = 'videos'
        self.idname     = 'video_id'
        self.parts      = 'statistics'
        self.fields     = 'items(id,statistics(viewCount))'

    def prune(self):            super().prune()
    def execution_time(self):   super().execution_time()
    def freeze(self):           super().freeze()
    def get_items(self):        super().get_items()
    def get_sql(self):          super().get_sql()
    def query_api(self):        super().query_api()
    def release(self,item_id):  super().release(item_id)
    def unavailable(self):      super().unavailable()
    def update_query(self):     super().update_query()

    def tune_sql(self):
        timespan_01 = (datetime.datetime.now() - datetime.timedelta(days = 1)).strftime('%Y-%m-%d')
        timespan_02 = "','".join( [(datetime.datetime.now() - datetime.timedelta(days = d)).strftime('%Y-%m-%d') for d in [1,2,3,4,5,6,7,14,21,28,60]])
        self.sql = self.sql.replace('{timespan_01}', timespan_01).replace( '{timespan_02}', timespan_02)

    def code_sql(self):
        return '''
             select v.video_id
             from video v
             join pipeline p on p.video_id = v.video_id
             left join flow as fl on fl.video_id = v.video_id
             left join video_stat_02 vs on ( (vs.video_id = v.video_id) and (vs.viewed_at > '{timespan_01}'))
             where v.pubdate in ('{timespan_02}')
                and fl.id is null
                and vs.id is null
                and p.status = 'active'
                and ((p.lang = 'fr') or (p.lang is null))
         '''

    def decode(self):
        super().decode()
        self.df['source']    = 'api'
        self.df['viewed_at'] = datetime.datetime.now().strftime('%Y-%m-%d')

    def ingest(self):
        print(f"== {self.df.shape} to insert")
        for i,d in self.df.iterrows():
            VideoStat.insert(d)
            self.release(d.video_id)







# -----------------
