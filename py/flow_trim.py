from .flow import *
from .flow_video_stats import *
from .flow_channel_stats import *
from .flow_channel_topics import *
from .flow_complete_videos import *
from .flow_complete_channels import *

class FlowTrim(Flow):

    def __init__(self,**kwargs):
        self.flowname   = 'trim'
        kwargs['mode']  = 'local'
        super().__init__(**kwargs)
        self.operations = ['helm','trim']
        self.trim_tasks = ['enforce_border','set_pubdate','flow_cleanup','helm_cleanup','cold_videos']
        self.helm_tasks = pd.read_sql("select queryname from query", job.db.conn)['queryname'].values

    def execution_time(self):   super().execution_time()
    def code_sql(self): pass

    def helm(self):
        print("==" * 5, "helm")
        for task in self.helm_tasks:
            try:
                start_time      = datetime.datetime.now()
                classname = 'Flow'+ ''.join(word.title() for word in task.split('_'))
                klass = globals()[classname]
                tk = klass(flowtag = False, mode = 'dbquery', counting = True)
                tk.get_items()
                print(f"- {task}: \t", tk.data.shape[0], f"rows \t {(datetime.datetime.now() - start_time).total_seconds()}s")
                sql = f'''
                    insert into helm (jobname, count_, created_at)
                    values ('{task}', {tk.data.shape[0]}, now())
                '''
                job.execute(sql)
            except:
                pass

    def trim(self):
        print("==" * 5, "trim")
        for task in self.trim_tasks:
            job.execute(  getattr(self, f"sql_{task}")() )
            print(f"- {task}: {job.db.cur.rowcount} rows")

    def sql_enforce_border(self):
        '''
            All channels with a country != FR, Null, '' are inserted into border
        '''
        return '''
            insert into border (channel_id)
            (select ch.channel_id
                from channel ch
                left join border b on b.channel_id = ch.channel_id
                where ch.country in (
                    select distinct country
                    from channel
                    where (country is not null) and (country !='') and (country != 'FR')
                ) and b.id is null
            )
            on conflict (channel_id) DO NOTHING
        '''

    def sql_set_pubdate(self):
        '''
            The video.published_at datetime can changes and sometimes leads to weird video.pubdate
            This query resets the video.pubdate correctly
        '''
        return '''
            update video
            set pubdate = to_char(published_at ,'YYYY-MM-DD')
            where video_id in (
                select video_id from video
                where pubdate != to_char(published_at ,'YYYY-MM-DD')
                and published_at is not null)
        '''

    def sql_flow_cleanup(self):
        '''
            items in flow for over an hour are released
        '''
        return "delete from flow where start_at < now() - interval '1 hour'"

    def sql_helm_cleanup(self):
        '''
            only 48h of helm data is kept
        '''
        return "delete from helm where created_at < now() - interval '48 hours'"

    def sql_cold_videos(self):
        '''
        Videos that are older than 6 months are set to cold status
        '''
        return '''
            update pipeline set status = 'cold'
            where video_id in
                (select v.video_id
                    from video v
                    join pipeline pp on pp.video_id = v.video_id
                    where pp.status = 'active'
                    and v.published_at < now() - interval '6 months'
                    limit 100
                )
        '''



# -----------------
