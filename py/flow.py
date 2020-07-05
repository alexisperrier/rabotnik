from .job import *
from .model import *
import pandas as pd
import datetime

class Flow(object):

    def __init__(self, **kwargs):
        self.start_time = datetime.datetime.now()
        self.mode       = kwargs['mode']
        self.counting   = kwargs['counting']
        self.flowtag    = kwargs['flowtag']
        self.max_items  = 50
        self.get_sql()

    def code_sql(self): pass
    def ingest(self):   pass

    def update_query(self):
        self.mode = 'script'
        self.get_sql()
        sql = f'''update query set sql = $${self.sql}$$ where queryname = '{self.flowname}';'''
        job.execute(sql)

    def release(self, item_id):
        # rm item_id from flow
        sql = f'''
            delete from flow where {self.idname} = '{item_id}' and flowname = '{self.flowname}'
        '''
        job.execute(sql)

    def freeze(self):
        # add item_ids to flow, do nothing if item_id already in flow
        for item_id in self.item_ids:
            sql = f'''
                insert into flow ({self.idname}, flowname,start_at)
                values ('{item_id}','{self.flowname}',now())
                on conflict ({self.idname}, flowname) DO NOTHING;
            '''
            job.execute(sql)

    def get_items(self):
        '''
            data is a dataframe with potentially multiple columns
            number of samples may not be bounded by self.max_items
            whereas item_ids is the list of video_ids or channel_ids
            that are processed or sent to the API
        '''
        self.data       = pd.read_sql(self.sql, job.db.conn)
        self.item_ids   = list(self.data[:min([self.max_items, self.data.shape[0]])][self.idname].values)
        # add forced updates at the top of the pile for immediate processing
        sql = f''' select {self.idname} from flow where flowname = '{self.flowname}' and mode = 'forced' '''
        tmp = pd.read_sql(sql, job.db.conn)
        if tmp.shape[0]> 0:
            self.item_ids = list(tmp[self.idname].values) + self.item_ids
            self.item_ids = self.item_ids[:min([self.max_items, len(self.item_ids) ]) ]
        print(f"{len(self.item_ids)} {self.idname}")


    def get_sql(self):
        '''
        the sql of reference, used to get the items, is stored in the dabase in the query table
        the sql from code_sql() can be used in conjonction with the Flow.update_query() method
        to update the query in the database
        '''
        if self.mode == 'dbquery':
            job.execute(f" select sql from query where queryname = '{self.flowname}' ")
            self.sql = job.db.cur.fetchone()[0]
        else:
            self.sql = self.code_sql()

        if not self.counting:
            self.sql = self.sql + f" limit {self.max_items}"

    def query_api(self):
        self.results = APIrequest(self,job).get()
        self.status_code = self.results.result.status_code
        self.ok = self.results.result.ok
        self.reason = self.results.result.reason


    def execution_time(self):
        self.delta_time = (datetime.datetime.now() - self.start_time).seconds
        print("-- "* 5 + "execution time {}m {}s".format(  int(self.delta_time / 60), str(self.delta_time -  int(self.delta_time / 60)*60).zfill(2) ))


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
        # self.max_items  = 50
        self.endpoint   = 'channels'
        self.idname     = 'channel_id'
        self.parts      = 'statistics'
        self.fields     = 'items(id,statistics(viewCount,subscriberCount,videoCount))'

    def execution_time(self):   super().execution_time()
    def freeze(self):           super().freeze()
    def get_items(self):        super().get_items()
    def get_sql(self):          super().get_sql()
    def query_api(self):        super().query_api()
    def release(self,item_id):  super().release(item_id)
    def update_query(self):     super().update_query()

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

    def decode(self):
        '''
            Content returned by the API is transformed into a dataframe
        '''
        data = json.loads(self.results.result.content.decode('utf-8'))
        self.df = pd.io.json.json_normalize(data['items']).rename(columns = FlowChannelStats.varnames_api2db)

    def ingest(self):
        for i,d in self.df.iterrows():
            ChannelStat.upsert(d)
            self.release(d.channel_id)












# ------------
