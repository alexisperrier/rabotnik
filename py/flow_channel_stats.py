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

    def tune_sql(self):
        month_ago = (datetime.datetime.now() - datetime.timedelta(days = 30)).strftime('%Y-%m-%d')
        self.sql = self.sql.replace('{month_ago}', month_ago)

    def code_sql(self):
        return '''
            select ch.channel_id, to_char(cs.retrieved_at ,'YYYY-MM-DD') as statdate, ch.activity_score
            from channel ch
                join pipeline p on p.channel_id = ch.channel_id
                left join channel_stat cs on cs.channel_id = ch.channel_id
                left join flow as fl on fl.channel_id = ch.channel_id and fl.flowname = 'channel_stats'
            where fl.id is null
                and p.status = 'active'
                and ((cs.id is null) OR (to_char(cs.retrieved_at ,'YYYY-MM-DD') = '{month_ago}'))
            order by ch.activity_score desc
        '''

        # return '''
        #     select cs.channel_id, cs.retrieved_at
        #     from channel_stat cs
        #     left join flow as fl on fl.channel_id = cs.channel_id and fl.flowname = 'channel_stats'
        #     join collection_items ci on ci.channel_id = cs.channel_id
        #     join pipeline p on p.channel_id = cs.channel_id
        #     where cs.retrieved_at < now() - interval '1 day'
        #     and p.status != 'unavailable'
        #     order by cs.retrieved_at
        #  '''


    def ingest(self):
        for i,d in self.df.iterrows():
            ChannelStat.upsert(d)
