'''
Feed parsing
'''
from .flow import *
from .text import *
import datetime, time
import feedparser

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
        self.operations = ['get_items','parse','ingest']

    def execution_time(self):   super().execution_time()
    def freeze(self):           super().freeze()
    def get_items(self):        super().get_items()
    def get_sql(self):          super().get_sql()
    def query_api(self):        super().query_api()
    def release(self,item_id):  super().release(item_id)
    def update_query(self):     super().update_query()
    def tune_sql(self):         pass

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

    def parse(self):

        channels = []
        videos   = {}

        for channel_id in self.item_ids:
            result    = feedparser.parse( FlowFeedParsing.BASE_URL +  channel_id )

            if (result.status == 200) & (len(result.entries) > 0):
                entries = pd.io.json.json_normalize(result.entries)[self.__class__.varnames_feed2db.keys()]
                entries.rename(columns = self.__class__.varnames_feed2db, inplace = True)
                entries['origin']       = 'feed_parsing'
                entries['source']       = 'rss'
                entries['viewed_at']    = datetime.datetime.now().strftime('%Y-%m-%d')
                entries['title']        = entries.title.apply(lambda d : TextUtils.valid_string_db(d) )
                entries['summary']      = entries.summary.apply(lambda d : TextUtils.valid_string_db(d) )

                entries.sort_values(by = 'published_at', ascending = False, inplace = True)
                entries.reset_index(inplace = True, drop = True)

                videos[channel_id]= entries
                frequency, channel_status, activity_score = self.__class__.activity_score(entries)

            elif (result.status == 200) & (len(result.entries) == 0):
                print("empty feed")
                frequency, channel_status, activity_score = '30 days', 'empty_feed', 0
            else:
                print("feed error", result.status, result.bozo)
                frequency, channel_status, activity_score = '100 years', 'feed_error', 0

            channels.append({
                'channel_id' : channel_id,
                'status_code': result.status,
                'ok'         : (result.status == 200) & (len(result.entries) > 0),
                'reason'     : result.bozo,
                'frequency'  : frequency,
                'channel_status'  : channel_status,
                'activity_score'  : activity_score
            })

        self.channels = pd.DataFrame(channels)
        self.videos   = videos

    def ingest(self):
        videos_created  = 0
        n_feed_error    = 0
        n_stat          = 0
        
        for i,d in self.channels.iterrows():
            if not d.ok:
                n_feed_error +=1
                print("======= channel feed not ok")
                print(d)

            Timer.update_channel_from_feed(d)
            Pipeline.update_channel_from_feed(d)
            self.release(d.channel_id)

        for channel_id, videos in self.videos.items():
            print("==\t",channel_id)
            # get list of videos already in the db
            sql = f'''
                select video_id from video where video_id in ('{"','".join(videos.video_id.values)}')
            '''
            existing_video_ids = pd.read_sql(sql, job.db.conn).video_id.values

            for i,d in videos.iterrows():
                n_stat += VideoStat.create(d)
                if d.video_id not in existing_video_ids:
                    n_created = Video.create(d)
                    if n_created > 0:
                        print("--", d.video_id, d.title[:100])
                    videos_created += n_created
                    Pipeline.create(idname = 'video_id',item_id = d.video_id)
                    Timer.create(idname = 'video_id',item_id = d.video_id)

        print(f"{videos_created} new videos \t {n_feed_error} feed errors \t {n_stat} new video stats")

    @classmethod
    def activity_score(cls,entries):
        n_videos = entries.shape[0]
        if n_videos == 0:
            return '30 days', 'empty_feed', 0

        recent  =  time.mktime( entries.loc[0].published_parsed )
        oldest  =  time.mktime( entries.loc[ n_videos - 1 ].published_parsed )
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

        return frequency, channel_status, activity_score






# -----------------
