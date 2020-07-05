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
        self.tune_sql()

    def code_sql(self): pass
    def ingest(self):   pass
    def tune_sql(self): pass

    def decode(self):
        '''
            Content returned by the API is transformed into a dataframe with proper column names
        '''
        data = json.loads(self.results.result.content.decode('utf-8'))
        self.df = pd.io.json.json_normalize(data['items']).rename(columns = self.__class__.varnames_api2db)


    def execution_time(self):
        self.delta_time = (datetime.datetime.now() - self.start_time).seconds
        print("--"* 5 + "execution time {}m {}s".format(  int(self.delta_time / 60), str(self.delta_time -  int(self.delta_time / 60)*60).zfill(2) ))

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

    def prune(self):
        '''
            not all item_ids are returned by the API, videos can be deleted, channels can be banned
            => tag item as pipeline status: unavailable
            => rm from flow
        '''
        deleted_ids     = [id for id in self.item_ids if id not in self.df[self.idname].values  ]
        print(f"{len(deleted_ids)} unaccessible items: {deleted_ids}")

        for item_id in deleted_ids[:1]:
            print(item_id)
            sql = f" update pipeline set status = 'unavailable' where {self.idname} = '{item_id}' "
            job.execute(sql)

            self.release(item_id)

    def query_api(self):
        self.results = APIrequest(self,job).get()
        self.status_code = self.results.result.status_code
        self.ok = self.results.result.ok
        self.reason = self.results.result.reason

    def release(self, item_id):
        # rm item_id from flow
        sql = f'''
            delete from flow where {self.idname} = '{item_id}' and flowname = '{self.flowname}'
        '''
        job.execute(sql)

    def update_query(self):
        self.mode = 'script'
        self.get_sql()
        sql = f'''update query set sql = $${self.sql}$$ where queryname = '{self.flowname}';'''
        job.execute(sql)














# ------------
