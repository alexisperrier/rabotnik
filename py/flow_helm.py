from .flow import *
from .flow_video_stats import *
from .flow_channel_stats import *
from .flow_channel_topics import *
from .flow_complete_videos import *
from .flow_complete_channels import *
from .flow_feed_parsing import *
from .flow_index_search import *
from .flow_scrape import *

class FlowHelm(Flow):
    def __init__(self,**kwargs):
        self.flowname   = 'helm'
        kwargs['mode']  = 'local'
        super().__init__(**kwargs)
        self.operations = ['helm']
        self.helm_tasks = pd.read_sql("select queryname from query order by queryname asc", job.db.conn)['queryname'].values

    def execution_time(self):   super().execution_time()
    def code_sql(self): pass
    def get_sql(self): pass

    def helm(self):
        for task in self.helm_tasks:
            start_time      = datetime.datetime.now()
            klassname = 'Flow'+ ''.join(word.title() for word in task.split('_'))
            if klassname in globals().keys():
                klass = globals()[klassname]
                tk = klass(flowtag = False, mode = 'dbquery', counting = True)
                tk.get_items()
                print(f"- {task}: \t", tk.data.shape[0], f"rows \t {(datetime.datetime.now() - start_time).total_seconds()}s")
                sql = f'''
                    insert into helm (jobname, count_, created_at)
                    values ('{task}', {tk.data.shape[0]}, now())
                '''
                job.execute(sql)
            else:
                print(f"====== {klassname} not in globals().keys() =====")






# ----
