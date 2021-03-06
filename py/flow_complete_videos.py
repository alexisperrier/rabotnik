'''
Gets video data from Youtube API
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
        self.operations = ['get_items', 'freeze', 'query_api', 'decode', 'prune', 'ingest', 'postop', 'bulk_release']

    def code_sql(self):
        '''
        The condition on v.published_at excludes v.published_at = null
        videos from scrape: recommended videos are not completed
        but channels from recommended videos and related channels are.
        '''
        return '''
            select v.video_id, v.published_at, v.origin, p.status, pch.status, pch.id
            from video v
                join pipeline p on p.video_id = v.video_id
                left join pipeline pch on pch.channel_id = v.channel_id
                left join flow as fl on (fl.video_id = v.video_id and fl.flowname = 'complete_videos')
            where p.status = 'incomplete'
            and (pch.status = 'active' or pch.id is null)
            and fl.id is null
            and ((v.published_at > now() - interval '1 month') or (v.published_at is null))
            order by v.origin asc, v.published_at desc
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
            self.df['title']      = self.df.title.apply(lambda d : TextUtils.to_db(d) )
            self.df['summary']    = self.df.summary.apply(lambda d : TextUtils.to_db(d) )
            self.df['wikitopics'] = self.df.topic_categories.apply(lambda d : TextUtils.extract_topic_categories(d))

    def ingest(self):
        print(f"== {self.df.shape} videos to update")
        for i,d in self.df.iterrows():
            Video.update(d)

            sql = f'''
                select status from pipeline where channel_id = '{d.channel_id}'
            '''
            job.execute(sql)
            if job.db.cur.rowcount >0:
                channel_status = job.db.cur.fetchone()[0]
            else:
                channel_status = None
            print(d.video_id, d.channel_id, channel_status)
            if channel_status in ['active','incomplete']:
                VideoScrape.insert(d.video_id)
                Pipeline.update_status(idname = 'video_id',  item_id = d.video_id, status = 'active')
            elif channel_status == 'foreign':
                Pipeline.update_status(idname = 'video_id',  item_id = d.video_id, status = 'foreign')
            elif channel_status in ['unavailable', 'feed_error','feed_empty']:
                Pipeline.update_status(idname = 'video_id',  item_id = d.video_id, status = 'inactive_channel')
            else:
                Pipeline.update_status(idname = 'video_id',  item_id = d.video_id, status = 'unknown_channel')

    def postop(self):
        '''
            Checks the existence of the channels
        '''
        print("======= postop")
        if (not self.df.empty):
            channel_count = 0
            channel_ids = self.df.channel_id.unique()
            sql = f'''
                select channel_id, title from channel where channel_id in ('{"','".join(channel_ids)}')
            '''
            existing_channels = pd.read_sql(sql, job.db.conn)
            print("--"*5)
            print("existing_channels")
            print(existing_channels)
            existing_channel_ids = existing_channels.channel_id.values
            missing_channel_ids = [id for id in channel_ids if id not in existing_channel_ids]

            data = self.df[self.df.channel_id.isin(missing_channel_ids)].copy()

            print("--missing_channel_ids:\t",missing_channel_ids)
            for i,d in data.iterrows():
                channel_count += Channel.create(d.channel_id, 'recommended videos')
                Pipeline.create(idname = 'channel_id',item_id = d.channel_id)
            print(f"{channel_count} related channels created")









# -----------------
