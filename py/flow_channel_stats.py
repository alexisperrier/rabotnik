from .flow import *

class FlowChannelStats(Flow):

    varnames_api2db = {
        'id': 'channel_id',
        'statistics.viewCount': "views",
        'statistics.subscriberCount': "subscribers",
        'statistics.videoCount': "videos"
    }

    def __init__(self,**kwargs):
        self.flowname = 'channel_stats'
        super().__init__(**kwargs)
        self.endpoint   = 'channels'
        self.idname     = 'channel_id'
        self.parts      = 'statistics'
        self.fields     = 'items(id,statistics(viewCount,subscriberCount,videoCount))'

    def decode(self):           super().decode()
    def prune(self):            super().prune()
    def execution_time(self):   super().execution_time()
    def freeze(self):           super().freeze()
    def get_items(self):        super().get_items()
    def get_sql(self):          super().get_sql()
    def query_api(self):        super().query_api()
    def release(self,item_id):  super().release(item_id)
    def update_query(self):     super().update_query()
    def tune_sql(self):         super().tune_sql()

    def code_sql(self):
        return '''
            select ch.channel_id
            from channel ch
                join pipeline p on p.channel_id = ch.channel_id
                join timer t on t.channel_id = ch.channel_id
                left join border b on b.channel_id = ch.channel_id
                left join channel_stat cs on cs.channel_id = ch.channel_id
                left join flow as fl on fl.channel_id = ch.channel_id and fl.flowname = 'channel_stats'
            where fl.id is null
                and b.id is null
                and ((t.rss_next_parsing < now() ) or (t.rss_next_parsing is null))
                and p.status in ('active','energised','frenetic','sluggish','steady','asleep','cold','dormant','blank')
                and p.channel_complete
                and ((cs.id is null) OR (cs.retrieved_at < NOW() - interval '1 month'))
            order by t.rss_next_parsing desc
        '''

    def ingest(self):
        for i,d in self.df.iterrows():
            ChannelStat.upsert(d)
            self.release(d.channel_id)
