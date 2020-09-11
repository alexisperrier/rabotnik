'''
see https://developers.google.com/youtube/v3/docs/videos#resource
'''
from .flow import *
import datetime
import isodate
from .text import *

class FlowVideoSearch(Flow):

    varnames_api2db = {
        'id.videoId':           'video_id',
        'snippet.publishedAt':  'published_at',
        'snippet.channelId':    'channel_id',
        'snippet.title':        'title',
        'snippet.description':  'summary',
        'snippet.thumbnails.default.url':'thumbnail'
    }

    def __init__(self,**kwargs):
        job.config['offset_factor'] = 0
        self.max_items  = 1000
        self.flowname = 'video_search'
        super().__init__(**kwargs)
        self.since_days = 2
        self.endpoint   = 'search'
        self.parts      = 'snippet'

        self.operations = ['get_items','query_api_decode','ingest']
        self.fields     = f"items(id,snippet(publishedAt,channelId,title,description,thumbnails/default/url))"

    def code_sql(self):
        return '''
            select src.collection_id, src.id as search_id, src.keywords from searches src where src.behavior = 'dynamic';
         '''

    def get_items(self):
        self.data       = pd.read_sql(self.sql, job.db.conn)
        self.keywords   = list(self.data[:min([self.max_items, self.data.shape[0]])]['keywords'].values)

    def query_api_decode(self):
        self.df = pd.DataFrame()

        for keyword in self.keywords:

            self.keyword = keyword
            results = APIrequest(self,job).get()

            if results.result.ok:
                data    = json.loads(results.result.content.decode('utf-8'))
                # df      = pd.io.json.json_normalize(data['items']).rename(columns = self.__class__.varnames_api2db)
                df      = pd.json_normalize(data['items']).rename(columns = self.__class__.varnames_api2db)
                df['origin'] = f"search {keyword}"
                df['keyword'] = keyword
                self.df = pd.concat([self.df, df], sort=False)
                print(f" [{keyword}] {df.shape[0]} results")
            else:
                print(f"results.result.status_code {results.result.status_code} reason {results.result.reason}")
                self.status_code = results.result.status_code
                self.reason = results.result.reason
                self.ok = False
                break;
        # drop duplicates
        self.df = self.df.drop_duplicates(subset = ['video_id']).reset_index(drop = True)
        # lang detection
        ld = LangDetector()
        self.df['lang'] = self.df.apply(lambda d : ld.predict( ' '.join([d.title, d.summary]))['lang'],  axis = 1)
        print(f"{self.df.shape[0]} videos found\n {self.df[['title','lang']]}\n")
        self.df = self.df[self.df.lang == 'fr' ].reset_index(drop = True)

        print(f"== {self.df.shape[0]} videos found")


    def ingest(self):
        print(f"== {self.df.shape} to insert")
        videos_created = 0
        video_ids = self.df.video_id.unique()

        sql = f'''
            select video_id from video where video_id in ('{"','".join(video_ids)}')
        '''
        existing_video_ids = pd.read_sql(sql, job.db.conn).video_id.values

        missing_video_ids  = [id for id in video_ids if id not in existing_video_ids]

        print(f"-- {len(missing_video_ids)}  missing_videos: ",missing_video_ids)

        new_videos = self.df[self.df.video_id.isin(missing_video_ids)].reset_index(drop = True)

        for i,d in new_videos.iterrows():
            n_created = Video.create_from_feed(d)
            if n_created > 0:
                print("++", d.video_id, d.title[:100])
            videos_created += n_created
            Pipeline.create(idname = 'video_id',item_id = d.video_id)

        print(f"== {videos_created} new videos from search")

        print("--"*5, "search channel creation")
        channel_count = 0
        channel_ids = self.df.channel_id.unique()

        sql = f'''
            select channel_id, title from channel where channel_id in ('{"','".join(channel_ids)}')
        '''
        existing_channel_ids = pd.read_sql(sql, job.db.conn).channel_id.values
        missing_channel_ids  = [id for id in channel_ids if id not in existing_channel_ids]

        print(f"-- {len(missing_channel_ids)} missing channels: ",missing_channel_ids)
        new_channels = self.df[self.df.channel_id.isin(missing_channel_ids)].reset_index(drop = True)
        new_channels = new_channels.drop_duplicates(subset = ['channel_id']).reset_index(drop = True)
        for i,d in new_channels.iterrows():
            print("++", d.channel_id)
            channel_count += Channel.create(d.channel_id, d.origin)
            Pipeline.create(idname = 'channel_id',item_id = d.channel_id)

        print(f"== {channel_count} new channels from search ")

        print("--"*5, "add videos to collections")
        videos_count = 0
        for i,d in self.data.iterrows():
            cond = self.df.keyword == d.keywords
            for k,v in self.df[cond].iterrows():
                sql = f'''
                    insert into collection_items (collection_id, search_id, video_id, created_at, updated_at)
                    values
                    ({d.collection_id}, {d.search_id}, '{v.video_id}', now(), now())
                    on conflict (collection_id, video_id) DO NOTHING;
                '''
                job.execute(sql)
                videos_count += job.db.cur.rowcount

        print(f"== {videos_count} added to collections")


# -----------------
