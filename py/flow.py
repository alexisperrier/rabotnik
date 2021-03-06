from .job import *
from .model import *
import pandas as pd
import numpy as np
import datetime

class Flow(object):
    '''
    Base class for all flows with default methods
    '''

    def __init__(self, **kwargs):
        self.start_time = datetime.datetime.now()
        self.mode       = kwargs['mode']
        self.counting   = kwargs['counting']
        self.flowtag    = kwargs['flowtag']

        if not hasattr(self, 'max_items'):
            self.max_items  = kwargs['max_items']

        self.ok         = True
        self.channel_growth = job.channel_growth
        self.operations = ['get_items','freeze','query_api','decode','prune','ingest','bulk_release']
        self.get_sql()
        self.tune_sql()

    # implements local query def in flows. Used to bypass, update and test query stored in db
    def code_sql(self): pass
    # insert results into db
    def ingest(self):   pass
    # any secondary task
    def postop(self):   pass
    # builds sql query when parameters
    def tune_sql(self): pass

    def decode(self):
        '''
            Content returned by the API is transformed into a dataframe with proper column names
        '''
        data = json.loads(self.results.result.content.decode('utf-8'))

        if 'items' in data.keys():
            # self.df = pd.io.json.json_normalize(data['items']).rename(columns = self.__class__.varnames_api2db)
            self.df = pd.json_normalize(data['items']).rename(columns = self.__class__.varnames_api2db)
        else:
            self.df = pd.DataFrame(columns = [self.idname])

    def execution_time(self):
        self.delta_time = (datetime.datetime.now() - self.start_time).seconds
        print("--"* 5 + " \t execution time {}m {}s".format(  int(self.delta_time / 60), str(self.delta_time -  int(self.delta_time / 60)*60).zfill(2) ))

    def freeze(self):
        '''
        freezes videos and channels for a certain task (flow)
        to make them unavailable for processing for the same task from other instances
        '''
        if self.flowtag:
            print("-- start freeze")
            for item_id in self.item_ids:
                sql = f'''
                    insert into flow ({self.idname}, flowname,start_at)
                    values ('{item_id}','{self.flowname}',now())
                    on conflict ({self.idname}, flowname) DO NOTHING;
                '''
                job.execute(sql)
            print("-- freeze done")

    def get_items(self):
        '''
            runs the sql query to find videos and channels that need to be processed

            'data' is a dataframe with potentially multiple columns
            number of samples may not be bounded by self.max_items
            whereas item_ids is the list of video_ids or channel_ids
            that are processed or sent to the API
        '''
        self.data       = pd.read_sql(self.sql, job.db.conn)
        self.item_ids   = list(self.data[:min([self.max_items, self.data.shape[0]])][self.idname].values)
        # add forced updates at the top of the pile for immediate processing
        if job.forced_flow:
            print("======= handling forced items in flow")
            sql = f''' select {self.idname} from flow where flowname = '{self.flowname}' and mode = 'forced' '''
            tmp = pd.read_sql(sql, job.db.conn)
            self.forced = tmp
            print(f"-- {tmp.shape} forced items {self.idname} ")
            if tmp.shape[0]> 0:
                self.item_ids = list(tmp[self.idname].values) + self.item_ids
                self.item_ids = self.item_ids[:min([self.max_items, len(self.item_ids) ]) ]

        if not self.counting:
            print(f"{len(self.item_ids)} items")
        self.ok = len(self.item_ids) > 0
        self.reason = 'No more items'
        print(f" {len(self.item_ids)} items")
        print(self.item_ids)

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


        # offset factor is set according to the hosting instance
        if self.sql is not None:
            if not self.counting:
                self.sql = self.sql + f" limit {self.max_items}"
            if job.config['offset_factor'] > 0:
                self.sql = self.sql + f" offset {self.max_items * job.config['offset_factor']}"


    def prune(self):
        '''
            not all item_ids are returned by the API, videos can be deleted, channels can be banned
            => tag item as pipeline status: unavailable
            => rm from flow
        '''
        if self.df.empty:
            deleted_ids = self.item_ids
        else:
            deleted_ids     = [id for id in self.item_ids if id not in self.df[self.idname].values  ]
        print(f"{len(deleted_ids)} unaccessible items: {deleted_ids}")

        for item_id in deleted_ids:
            Pipeline.update_status(idname = self.idname, item_id = item_id, status = 'unavailable')
            # self.release(item_id)

    def query_api(self):
        '''
        Queries the Youtube API V3
        '''
        self.results     = APIrequest(self,job).get()
        self.status_code = self.results.result.status_code
        self.ok          = self.results.result.ok
        self.reason      = self.results.result.reason

    def release(self, item_id):
        '''
            rm single item_ids from the flow table. see freeze()
        '''
        sql = f'''
            delete from flow where {self.idname} = '{item_id}' and flowname = '{self.flowname}'
        '''
        job.execute(sql)

    def bulk_release(self):
        '''
            rm all the item_id from the flow table for a given flow
        '''
        if  hasattr(self, 'forced'):
            sql = f'''
                delete from flow where flowname = '{self.flowname}'
                    and {self.idname} in  ('{"','".join(self.forced[self.idname].values)}')
                    and mode = 'forced'
            '''
            job.execute(sql)
            return job.db.cur.rowcount
        else:
            return 0

    def update_query(self):
        '''
            updates the query in the db by the query defined in code_sql()
        '''
        self.mode = 'script'
        self.get_sql()
        sql = f'''update query set sql = $${self.sql}$$ where queryname = '{self.flowname}';'''
        job.execute(sql)














# ------------
