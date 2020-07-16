from .flow import *

class FlowCare(Flow):

    def __init__(self,**kwargs):
        self.flowname   = 'care'
        kwargs['mode']  = 'local'
        kwargs['counting']  = True
        super().__init__(**kwargs)
        self.operations = ['care']
        self.care_tasks = ['enforce_border','enforce_lang','set_pubdate','check_pubdate','flow_cleanup','helm_cleanup','cold_videos']

    def execution_time(self):   super().execution_time()
    def code_sql(self): pass

    def care(self):
        for task in self.care_tasks:
            job.execute(  getattr(self, f"sql_{task}")() )
            print(f"- {task}: \t{job.db.cur.rowcount} rows")

    def sql_enforce_border(self):
        '''
            All channels with a country != FR, Null, '' are inserted into border
        '''
        return '''
            update pipeline p
            set status = 'foreign'
            from channel ch
            where  p.channel_id = ch.channel_id
                and p.status = 'active'
                and (ch.country is not null) and (ch.country !='') and (ch.country != 'FR');
        '''

    def sql_enforce_lang(self):
        '''
            All channels with a country  Null, '' and lang !=fr and lang_conf > 02 are inserted into border
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
            This query sets the video.pubdate
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
