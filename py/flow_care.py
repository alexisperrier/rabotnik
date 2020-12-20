'''
- Counts number of items (videos, channels) need processing for a given flow.
- Enforces distinction between French and Foreign channels
- sets video
    - pubdate (string '2020-01-01')
    - lang
    - Foreign / French status

'''
from .flow import *

class FlowCare(Flow):

    def __init__(self,**kwargs):
        self.flowname   = 'care'
        kwargs['mode']  = 'local'
        kwargs['counting']  = True
        job.config['offset_factor'] = 0
        super().__init__(**kwargs)
        self.operations = ['quality','care']
        self.care_tasks = ['enforce_border','enforce_lang','set_pubdate','check_pubdate','flow_cleanup','helm_cleanup','cold_videos']
        self.max_items = 16

        self.quality_tasks = ['complete_videos','video_scrape','video_stats']

    def execution_time(self):   super().execution_time()
    def code_sql(self): pass

    def care(self):
        for task in self.care_tasks:
            job.execute(  getattr(self, f"sql_{task}")() )
            print(f"- {task}: \t{job.db.cur.rowcount} rows")

    def sql_enforce_border(self):
        '''
            All channels with a country != FR, Null, '' are set as Foreign
        '''
        return '''
            update pipeline p
            set status = 'foreign'
            from channel ch
            where  p.channel_id = ch.channel_id
                and p.status = 'active'
                and (ch.country is not null) and (ch.country !='') and (ch.country != 'FR') and (ch.country != 'RE');
        '''

    def sql_enforce_lang(self):
        '''
            All channels with
            - country  Null, ''
            - lang !=fr and lang_conf > 02 (FastText lang detector)
            are set as Foreign
        '''
        return '''
            update pipeline p
            set status = 'foreign'
            from channel ch
            where  p.channel_id = ch.channel_id
                and  (ch.country is null or ch.country = '')
                and p.status = 'active'
                and p.lang !='fr'
                and p.lang_conf > 0.2
        '''

    def sql_set_pubdate(self):
        '''
            This query sets the video.pubdate (string '2020-01-01') from timestamp published_at
        '''
        return '''
            update video
                set pubdate = to_char(published_at ,'YYYY-MM-DD')
                where video_id in (
                    select v.video_id
                    from video v
                    where v.pubdate is null
                    and v.published_at is not null
                    order by v.id asc
                );
            '''

    def sql_check_pubdate(self):
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
            only 48h of dashboard (helm) data is kept
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

    # ----------------------------------------------------------------
    #  Quality of videos in collections
    # ----------------------------------------------------------------
    def quality(self):
        print("--" * 20)
        print(" Quality" )
        print("--" * 20)
        for task in self.quality_tasks:
            idname, qsql = getattr(self, f"sql_{task}")()
            data = pd.read_sql(qsql, job.db.conn)
            print(f"- {task}: \t{data.shape} rows")
            for i, d in data.iterrows():
                sql = f''' insert into flow ({idname}, flowname, mode, start_at)
                    values ('{d[idname]}', '{task}','forced', now())
                    on conflict ({idname}, flowname) DO NOTHING
                 '''
                job.execute(sql)

    def sql_complete_videos(self):
        return  'video_id',f'''
            select col.video_id
            from collection_items col
            join pipeline p on p.video_id = col.video_id
            join video v on v.video_id = col.video_id
            where v.duration is null
            and p.status != 'unavailable'
            order by col.video_id limit {self.max_items}
        '''

    def sql_complete_channels(self):
        return 'channel_id',f'''
            select ch.channel_id
            from channel ch
            join video v on v.channel_id = ch.channel_id
            where ch.title is null
            and v.video_id in (select distinct video_id from collection_items)
            order by ch.channel_id limit {self.max_items}
        '''

    def sql_video_stats(self):
        return 'video_id',f'''
            select col.video_id
            from collection_items col
            join pipeline p on p.video_id = col.video_id
            left join video_stat vs on vs.video_id = col.video_id
            where vs.video_id is null
            and p.status != 'unavailable'
            order by col.video_id limit {self.max_items}
        '''

    def sql_video_scrape(self):
        return 'video_id',f'''
            select col.video_id
            from collection_items col
            join pipeline p on p.video_id = col.video_id
            left join video_recommendations vr on vr.src_video_id = col.video_id
            where vr.src_video_id is null
            and p.status != 'unavailable'
            order by col.video_id limit {self.max_items}
        '''




# -----------------
