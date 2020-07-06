from .job import *

class Model(object):
    def __init__(self):
        pass

class ChannelTopic(Model):

    @classmethod
    def upsert(cls,d):
        if d.topics is None:
            sql = f'''
                    insert into topic as tpc (channel_id,  topics, created_at)
                    values ('{d.channel_id}',Null, now())
                on conflict (channel_id) do update
                    set topics = Null, created_at = now()
                    where tpc.channel_id = '{d.channel_id}'
            '''
        else:
            sql = f'''
                    insert into topic as tpc (channel_id,  topics, created_at)
                    values ('{d.channel_id}','{d.topics}', now())
                on conflict (channel_id) do update
                    set topics = '{d.topics}', created_at = now()
                    where tpc.channel_id = '{d.channel_id}'
            '''
        job.execute(sql)

class ChannelStat(Model):

    @classmethod
    def upsert(cls,d):
        sql = f'''
                insert into channel_stat as cs
                    (channel_id,  views, subscribers, videos, retrieved_at)
                values
                    ('{d.channel_id}', {d.views}, {d.subscribers}, {d.videos}, now())
            on conflict (channel_id) do update
                set views = {d.views},
                    subscribers = {d.subscribers},
                    videos = {d.videos},
                    retrieved_at = now()
                where cs.channel_id = '{d.channel_id}'
        '''
        job.execute(sql)

class VideoStat(Model):

    @classmethod
    def insert(cls,d):
        sql = f'''
                insert into video_stat_02 as cs
                    (video_id,  views, source, viewed_at)
                values
                    ('{d.video_id}', {d.views}, '{d.source}', '{d.viewed_at}')
        '''
        job.execute(sql)


class Video(Model):

    @classmethod
    def update(cls,d):
        sql = f'''
            update video set
                published_at = '{d.published_at}',
                channel_id = '{d.channel_id}',
                title = $${d.title}$$,
                summary = $${d.summary}$$,
                thumbnail = '{d.thumbnail}',
                category_id = {d.category_id},
                duration = '{d.duration}',
                caption = {d.caption},
                privacy_status = '{d.privacy_status}',
                tags = $${d.tags}$$,
                pubdate = '{d.pubdate}',
                live_content = '{d.live_content}',
                default_audio_language = '{d.default_audio_language}',
                default_language = '{d.default_language}',
                wikitopics = $${d.wikitopics}$$,
                seconds = {d.seconds},
                retrieved_at = now()
            where video_id = '{d.video_id}'
        '''
        job.execute(sql)


class Pipeline(Model):
    @classmethod
    def update_status(cls, **kwargs):
        sql = f" update pipeline set status = '{kwargs['status']}' where {kwargs['idname']}= '{kwargs['item_id']}' "
        job.execute(sql)

    @classmethod
    def create(cls, **kwargs):
        sql = f'''
                insert into pipeline ({kwargs['idname']}, status)
                values ('{kwargs['item_id']}','blank')
                on conflict ({kwargs['idname']}) DO NOTHING;
            '''
        job.execute(sql)

class Channel(object):
    @classmethod
    def create(cls, channel_id, origin ):
        sql = f'''
                insert into channel (channel_id, origin)
                values ('{channel_id}','{origin}')
                on conflict (channel_id) DO NOTHING;
            '''
        job.execute(sql)

    @classmethod
    def update(cls,d):
        sql = f'''
            update channel set
                created_at = '{d.created_at}',
                title       = $${d.title}$$,
                description = $${d.description}$$,
                thumbnail   = '{d.thumbnail}',
                show_related = '{d.show_related}',
                custom_url  = '{d.custom_url}',
                country     = '{d.country}',
                retrieved_at = now()
            where channel_id = '{d.channel_id}'
        '''
        job.execute(sql)


class Timer(Model):
    @classmethod
    def create(cls, **kwargs):
        sql = f'''
                insert into timer ({kwargs['idname']}, rss_next_parsing)
                values ('{kwargs['item_id']}',NOW())
                on conflict ({kwargs['idname']}) DO NOTHING;
            '''
        job.execute(sql)



class RelatedChannels(object):
     @classmethod
     def insert(cls, **kwargs):
         sql = f'''
                 insert into related_channels (channel_id, related_id, retrieved_at)
                 values ('{kwargs['channel_id']}','{kwargs['related_id']}',NOW())
                 on conflict (channel_id, related_id) DO NOTHING;
             '''
         job.execute(sql)


# -------
