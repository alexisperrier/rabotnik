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
        self.operations = ['get_items','freeze','parse','ingest','ingest_collections']

    def code_sql(self):
        return '''
            select ch.channel_id, col.collection_id
            from channel ch
            join pipeline p on p.channel_id  = ch.channel_id
            left join collection_items col on col.channel_id  = ch.channel_id
            left join flow as fl on fl.channel_id = ch.channel_id  and fl.flowname = 'feed_parsing'
            where ch.rss_next_parsing < now()
                 and p.status = 'active'
                 and p.lang = 'fr'
                 and fl.id is null
             order by ch.rss_next_parsing asc
         '''

    def parse(self):

        channels = []
        videos   = {}

        sql = f''' select channel_id, collection_id from collection_items  where channel_id in ('{"','".join(self.item_ids)}')  '''
        self.collections = pd.read_sql(sql, job.db.conn)
        print(f"self.collections {self.collections}")

        for channel_id in self.item_ids:
            result    = feedparser.parse( FlowFeedParsing.BASE_URL +  channel_id )

            if (result.status == 200) & (len(result.entries) > 0):
                entries = pd.io.json.json_normalize(result.entries)[self.__class__.varnames_feed2db.keys()]
                entries.rename(columns = self.__class__.varnames_feed2db, inplace = True)
                entries['origin']       = 'feed_parsing'
                entries['source']       = 'rss'
                entries['in_collection'] = channel_id in self.collections.channel_id.unique()

                entries['viewed_at']    = datetime.datetime.now().strftime('%Y-%m-%d')
                entries['title']        = entries.title.apply(lambda d : TextUtils.to_db(d) )
                entries['summary']      = entries.summary.apply(lambda d : TextUtils.to_db(d) )

                entries.sort_values(by = 'published_at', ascending = False, inplace = True)
                entries.reset_index(inplace = True, drop = True)

                videos[channel_id]= entries
                frequency, activity, activity_score = self.__class__.activity_score(entries)
                channel_status = 'active'

            elif (result.status == 200) & (len(result.entries) == 0):
                print("empty feed")
                frequency, activity, activity_score, channel_status = '30 days', None, None, 'feed_empty'
            else:
                print("feed error", result.status, result.bozo)
                frequency, activity, activity_score, channel_status = '1 week', None, None, 'feed_error'

            print(f"[{channel_id}] {frequency}, {activity}, {activity_score}, {channel_status} ")
            channels.append({
                'channel_id' : channel_id,
                'status_code': result.status,
                'ok'         : (result.status == 200) & (len(result.entries) > 0),
                'reason'     : result.bozo,
                'frequency'  : frequency,
                'channel_status'  : channel_status,
                'activity'  : activity,
                'activity_score'  : activity_score
            })

        self.channels = pd.DataFrame(channels)
        self.videos   = videos

    def ingest(self):
        videos_created  = 0
        n_feed_error    = 0
        n_stat          = 0
        # -------------------------------------
        #  Channel update
        # -------------------------------------
        for i,d in self.channels.iterrows():
            if not d.ok:
                n_feed_error +=1
                print("======= channel feed not ok")
                print(d)

            Channel.update_from_feed(d)
            Pipeline.update_status(idname = 'channel_id',  item_id = d.channel_id, status = d.channel_status)

        # -------------------------------------
        #  Videos
        # -------------------------------------
        for channel_id, videos in self.videos.items():
            print("\n==",channel_id)
            # get list of videos already in the db
            sql = f'''
                select video_id from video where video_id in ('{"','".join(videos.video_id.values)}')
            '''
            existing_video_ids = pd.read_sql(sql, job.db.conn).video_id.values

            for i,d in videos.iterrows():

                n_stat += VideoStat.create(d)
                if d.video_id not in existing_video_ids:
                    n_created = Video.create_from_feed(d)
                    if n_created > 0:
                        print("--", d.video_id, d.title[:100])
                    videos_created += n_created
                    Pipeline.create(idname = 'video_id',item_id = d.video_id)

        print(f"{videos_created} new videos \t {n_feed_error} feed errors \t {n_stat} new video stats")

    def ingest_collections(self):
        # -------------------------------------
        #  Collections
        # -------------------------------------
        print("====== insert into collections")
        n_collection = 0
        channel_ids = self.collections.channel_id.unique()
        for channel_id in channel_ids:
            collection_ids = self.collections[self.collections.channel_id == channel_id].collection_id.unique()
            videos = self.videos[channel_id]
            for collection_id in collection_ids:
                print(f"---- channel_id {channel_id} \tcollection_ids {collection_ids}\tcollection_id {collection_id}")
                for i,video in videos.iterrows():
                    sql = f'''
                        insert into collection_items (video_id, collection_id, origin, created_at, updated_at)
                        values
                        ('{video.video_id}', {collection_id}, 'feed_parsing', now(), now())  on conflict (video_id,collection_id) DO NOTHING;
                    '''
                    job.execute(sql)
                    n = job.db.cur.rowcount
                    n_collection += n
        print(f"== {n_collection} videos have been added to collections {self.collections.collection_id.unique()}")


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

        if entries.in_collection.all():
            activity  = 'active'
            frequency = '24 hours'
        elif age_recent > 180:          # 6 months since last video
            frequency   = '90 days'
            activity    = 'cold'
        elif age_recent > 90:           # 90 days since last video
            frequency   = '15 days'
            activity    = 'asleep'
        else:
            if activity_score <= 0.1:
                activity  = 'sluggish'
                frequency = '7 days'
            elif activity_score <= 0.5:
                activity  = 'steady'
                frequency = '3 day'
            elif activity_score <= 1:
                activity  = 'active'
                frequency = '24 hours'
            elif activity_score <= 5:
                activity  = 'energised'
                frequency = '12 hours'
            else:                       # more than 5 videos per day
                activity  = 'frenetic'
                frequency = '3 hours'

        return frequency, activity, activity_score






# -----------------
