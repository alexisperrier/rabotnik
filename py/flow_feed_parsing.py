'''
Feed parsing
'''
from .flow import *
import datetime
import isodate
from .text import *
import distutils.util

class FlowFeedParsing(Flow):

    BASE_URL = 'https://www.youtube.com/feeds/videos.xml?channel_id='
    varnames_feed2db = {
        'yt_videoid': 'video_id',
        'yt_channelid': 'channel_id',
        'title': 'title',
        'published': 'published_at',
        'published_parsed': 'published_parsed',
        'summary_detail.value': 'summary',
        'media_statistics.views': 'views'
    }

    def __init__(self,**kwargs):
        self.flowname = 'feed_parsing'
        super().__init__(**kwargs)
        self.idname = 'channel_id'
        self.max_items  = 2
        # self.operations = ['get_items','freeze','query_api','decode','prune','ingest']
        self.operations = ['get_items','freeze','parsing']
        # self.operations.append('postop')

    def prune(self):            super().prune()
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
            join pipeline p on p.channel_id  = ch.channel_id
            join timer t on t.channel_id = ch.channel_id
            left join border b on b.channel_id = ch.channel_id
            left join flow as fl on fl.channel_id = ch.channel_id
            where t.channel_id is not null
                 and ((t.rss_next_parsing < now() ) or (t.rss_next_parsing is null))
                 and t.error is null
                 and ((p.lang = 'fr') or (p.lang is null))
                 and p.status in ('active','energised','frenetic','sluggish','steady','asleep','cold','dormant','blank')
                 and p.channel_complete
                 and fl.id is null
                 and b.id is null
             order by t.rss_next_parsing asc
         '''

    def parsing(self):
        result    = feedparser.parse( FlowFeedParsing.BASE_URL +  self.channel_id )
        self.status_code = result.status
        self.ok          = (result.status == 200) & (len(result.entries) > 0)
        self.reason      = result.bozo
        self.videos      = result.entries

    def decode(self):
        self.df = pd.io.json.json_normalize(self.videos)[self.__class__.varnames_feed2db.keys()]
        self.df.rename(columns = self.__class__.varnames_feed2db, inplace = True)
        self.df['origin'] = 'feed_parsing'
        self.df.sort_values(by = 'published_at', ascending = False, inplace = True)
        self.df.reset_index(inplace = True, drop = True)

        self.activity_score()

    def ingest(self):
        # update pipeline and timer
        sql = f'''
            update pipeline
            set status = '{self.channel_status}',
                rss_frequency = '{self.rss_frequency}',
                activity_score = {self.activity_score}
            where channel_id = '{self.channel_id}'
        '''
        job.execute(sql)




        print(f"== {self.df.shape} to insert")
        # for i,d in self.df.iterrows():
        #     print(d.channel_id)
        #     Channel.update(d)
        #     Pipeline.update_status(idname = 'channel_id',  item_id = d.channel_id, status = 'active')
        #     sql = f"update pipeline set channel_complete = True where channel_id = '{d.channel_id}'"
        #     job.execute(sql)
        #     self.release(d.channel_id)

    def tune_sql(self):
        pass

    def activity_score(self):
        n_videos = self.df.shape[0]
        recent  =  time.mktime( self.df.loc[0].published_parsed )
        oldest  =  time.mktime( self.df.loc[ n_videos - 1 ].published_parsed )
        now     =  time.mktime(datetime.datetime.now().timetuple())

        age_recent      = divmod(now - recent, 24*3600)[0]
        n_days          = max(1,  divmod(now - oldest, 24*3600)[0] )
        activity_score  = np.round( n_videos / n_days, 2)

        # 6 months since last video
        if age_recent > 180:
            frequency = '90 days'
            channel_status = 'dormant'
        elif age_recent > 90:
            frequency = '15 days'
            channel_status = 'asleep'
        else:
            if activity_score <= 0.1:
                channel_status  = 'sluggish'
                frequency       = '3 days'
            elif activity_score <= 0.5:
                channel_status  = 'steady'
                frequency       = '1 day'
            elif activity_score <= 1:
                channel_status  = 'active'
                frequency       = '12 hours'
            elif activity_score <= 5:
                channel_status  = 'energised'
                frequency       = '6 hours'
            else: # more than 5 videos per day
                channel_status  = 'frenetic'
                frequency       = '2 hours'

        self.rss_frequency  = frequency
        self.channel_status = channel_status
        self.activity_score = activity_score






# -----------------
