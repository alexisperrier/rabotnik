'''
see https://developers.google.com/youtube/v3/docs/videos#resource
'''
from .flow import *
import datetime
import isodate
from .text import *

class FlowCompleteVideos(Flow):

    varnames_api2db = {
        'id': 'video_id',
        'snippet.publishedAt': 'published_at',
        'snippet.channelId': 'channel_id',
        'snippet.title': 'title',
        'snippet.description': 'summary',
        'snippet.thumbnails.default.url':'thumbnail',
        'snippet.tags': 'tags',
        'snippet.categoryId': 'category_id',
        'snippet.defaultAudioLanguage': 'default_audio_language',
        'snippet.defaultLanguage': 'default_language',
        'snippet.liveBroadcastContent': 'live_content',
        'contentDetails.duration': 'duration',
        'contentDetails.caption': 'caption',
        'status.privacyStatus': 'privacy_status',
        'topicDetails.topicCategories': 'topic_categories'
    }

    def __init__(self,**kwargs):
        self.flowname = 'complete_videos'
        super().__init__(**kwargs)
        self.endpoint   = 'videos'
        self.idname     = 'video_id'
        self.parts      = 'snippet,contentDetails,status,recordingDetails,topicDetails'
        snippet_str     = 'publishedAt,channelId,title,thumbnails/default/url,categoryId,tags,defaultAudioLanguage,defaultLanguage,description,liveBroadcastContent'
        status_str      = "privacyStatus,uploadStatus,rejectionReason"
        content_str     = 'duration,caption'
        self.fields     = f"items(id,snippet({snippet_str}),contentDetails({content_str}),status({status_str}),topicDetails(topicCategories),recordingDetails(location))"
        if self.channel_growth:
            self.operations.append('postop')

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
             select v.video_id, v.published_at, p.status
                 from video v
                 join pipeline p on p.video_id = v.video_id
                 left join border b on b.channel_id = v.channel_id
                 left join flow as fl on (fl.video_id = v.video_id and fl.flowname = 'complete_videos')
             where p.status = 'incomplete'
                 and b.id is null
                 and fl.id is null
         '''

    def decode(self):
        super().decode()
        if (not self.df.empty):
            self.df['pubdate'] = self.df.published_at.apply(lambda d: d.split('T')[0] )
            self.df['seconds'] = self.df.duration.apply(lambda d: isodate.parse_duration(d).seconds)
            for col in ['default_audio_language', 'default_language','tags', 'topic_categories']:
                if col in self.df.columns:
                    self.df.loc[self.df[col].isna(), col] = ''
                else:
                    self.df[col] = ''

            self.df.loc[self.df['live_content']== 'none', 'live_content'] = ''
            self.df['title']      = self.df.title.apply(lambda d : TextUtils.valid_string_db(d) )
            self.df['summary']    = self.df.summary.apply(lambda d : TextUtils.valid_string_db(d) )
            self.df['wikitopics'] = self.df.topic_categories.apply(lambda d : TextUtils.extract_topic_categories(d))

    def ingest(self):
        print(f"== {self.df.shape} to insert")
        for i,d in self.df.iterrows():
            print(d.video_id)
            Video.update(d)
            Pipeline.update_status(idname = 'video_id',  item_id = d.video_id, status = 'active')
            self.release(d.video_id)

    def tune_sql(self):
        pass

    def postop(self):
        '''
            Checks the existence of the channels
        '''
        print("======= postop")
        if (not self.df.empty):
            channel_ids = self.df.channel_id.unique()
            sql = f'''
                select channel_id from channel where channel_id in ('{"','".join(channel_ids)}')
            '''
            existing_channel_ids = pd.read_sql(sql, job.db.conn).channel_id.values
            missing_channel_ids = [id for id in channel_ids if id not in existing_channel_ids]

            data = self.df[self.df.channel_id.isin(missing_channel_ids)].copy()
            # find origin from videos
            sql     = f''' select video_id, origin from video where video_id in ('{"','".join(data.video_id.values)}') '''
            origins = pd.read_sql(sql, job.db.conn)
            data    = data.merge(origins, on = 'video_id', how = 'outer')

            print("--missing_channel_ids:\t",missing_channel_ids)
            for i,d in data.iterrows():
                print(d.channel_id, d.origin)
                Channel.create(d.channel_id, d.origin)
                Pipeline.create(idname = 'channel_id',item_id = d.channel_id)
                Timer.create(idname = 'channel_id',item_id = d.channel_id)









# -----------------
