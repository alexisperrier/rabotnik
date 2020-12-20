'''
Contain classes for most major database tables
Each class offers methods to insert, update, upsert ...

For instance the class Channel has the following methods:

- create: inserts a new channel in table channel
- update: updates data for a given channel_id, data is from API
- update_from_feed: updates data for a given channel_id, data is from RSS feed

'''
from .text import *
from .job import *
import datetime
import pytz
import urllib
from xml.etree import ElementTree
import html

class Model(object):
    # TODO rm, not used
    def __init__(self):
        pass


class Comment(Model):
    @classmethod
    def create(cls,d):
        try:
            sql = f'''
                    insert into comments (comment_id, video_id, discussion_id, parent_id,
                        author_name, author_channel_id,
                        text, reply_count, like_count,
                        published_at, created_at, updated_at)
                    values ('{d.comment_id}', '{d.video_id}', {d.discussion_id}, '{d.parent_id}',
                        $${TextUtils.to_db(d.author_name)}$$, '{d.author_channel_id}',
                        $${TextUtils.to_db(d.text)}$$, {d.reply_count}, {d.like_count},
                        '{d.published_at}', now(), now())
                        on conflict (comment_id) DO NOTHING
            '''
            job.execute(sql)
            return job.db.cur.rowcount
        except:
            return 0



class Discussion(Model):
    @classmethod
    def create(cls,d):
        try:
            sql = f'''
                    insert into discussions (video_id, total_results, results_per_page, error, created_at, updated_at)
                    values ('{d.video_id}', {d.total_results}, {d.results_per_page}, $${TextUtils.to_db(d.error)}$$, now(), now())
                    on conflict (video_id) DO NOTHING
                    RETURNING id;
            '''
            job.execute(sql)
            return job.db.cur.fetchone()[0]
        except:
            return None

class VideoStat(Model):

    @classmethod
    def create(cls,d):
        try:
            fields = "video_id, source, viewed_at"
            values = f"'{d.video_id}', '{d.source}', '{d.viewed_at}'"

            for field in ['views','like_count','dislike_count','favorite_count','comment_count']:
                if hasattr(d,field):
                    val = int(d[field])
                    fields += f",{field}"
                    values += f", {val}"
            sql = f'''
                    insert into video_stat as cs ({fields})
                    values ({values})
                    on conflict (video_id, viewed_at) DO NOTHING;
            '''
            job.execute(sql)
            return job.db.cur.rowcount
        except:
            return 0

class Channel(object):
    @classmethod
    def create(cls, channel_id, origin ):
        sql = f'''
                insert into channel (channel_id, origin)
                values ('{channel_id}','{origin}')
                on conflict (channel_id) DO NOTHING;
            '''
        job.execute(sql)
        return job.db.cur.rowcount

    @classmethod
    def update(cls,d):
        sql = f'''
            update channel set
                created_at  = '{d.created_at}',
                title       = $${TextUtils.to_db(d.title)}$$,
                description = $${TextUtils.to_db(d.description)}$$,
                thumbnail   = '{d.thumbnail}',
                show_related = '{d.show_related}',
                custom_url  = '{d.custom_url}',
                country     = '{d.country}',
                retrieved_at = now()
            where channel_id = '{d.channel_id}'
        '''
        job.execute(sql)
        return job.db.cur.rowcount

    @classmethod
    def update_from_feed(cls,d):


        if d.activity is not None:
            str_activity = f"activity = '{d.activity}',"
        else:
            str_activity = f"activity = null,"

        if d.activity is not None:
            str_activity_score = f"activity_score = {d.activity_score},"
        else:
            str_activity_score = f"activity_score = null,"

        sql = f'''
            update channel set
                {str_activity}
                {str_activity_score}
                rss_next_parsing = NOW() + interval '{d.frequency}',
                retrieved_at = now()
            where channel_id = '{d.channel_id}'
        '''
        job.execute(sql)
        return job.db.cur.rowcount

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
        if d.hidden_subscribers_count:
            sql = f'''
                    insert into channel_stat as cs
                        (channel_id,  views, videos, retrieved_at)
                    values
                        ('{d.channel_id}', {d.views}, {d.videos}, now())
                on conflict (channel_id) do update
                    set views = {d.views},
                        videos = {d.videos},
                        retrieved_at = now()
                    where cs.channel_id = '{d.channel_id}'
            '''
        else:
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
        return job.db.cur.rowcount

class IndexSearch(Model):
    @classmethod
    def upsert(cls,d):
        sql = f'''
                insert into augment as au (video_id, tsv_lemma, created_at)
                values ( '{d.video_id}', to_tsvector('french', $${TextUtils.to_db(d.refined_lemma)}$$), now() )
            on conflict (video_id) do update
                set tsv_lemma = to_tsvector('french', $${TextUtils.to_db(d.refined_lemma)}$$),
                    created_at = now()
                where au.video_id = '{d.video_id}'
        '''
        job.execute(sql)
        return job.db.cur.rowcount



class Video(Model):

    @classmethod
    def update(cls,d):
        sql = f'''
            update video set
                published_at = '{d.published_at}',
                channel_id = '{d.channel_id}',
                title = $${TextUtils.to_db(d.title)}$$,
                summary = $${TextUtils.to_db(d.summary)}$$,
                thumbnail = '{d.thumbnail}',
                category_id = {d.category_id},
                duration = '{d.duration}',
                caption = {d.caption},
                privacy_status = '{d.privacy_status}',
                tags = $${TextUtils.to_db(d.tags)}$$,
                pubdate = '{d.pubdate}',
                live_content = '{d.live_content}',
                default_audio_language = '{d.default_audio_language}',
                default_language = '{d.default_language}',
                wikitopics = $${TextUtils.to_db(d.wikitopics)}$$,
                seconds = {d.seconds},
                retrieved_at = now()
            where video_id = '{d.video_id}'
        '''
        try:
            job.execute(sql)
            return job.db.cur.rowcount
        except:
            print("=="*20)
            print("FAILED")
            print(sql)
            print("=="*20)
            job.reconnect()
            return 0

    @classmethod
    def create_from_feed(cls,d):
        # ok
        sql = f'''
            insert into video
                (video_id,channel_id,title,summary,origin,published_at)
            values
                ('{d.video_id}', '{d.channel_id}',$${TextUtils.to_db(d.title)}$$,$${TextUtils.to_db(d.summary)}$$,'{d.origin}','{d.published_at}')
            on conflict (video_id) DO NOTHING;
        '''
        job.execute(sql)
        return job.db.cur.rowcount

    @classmethod
    def create_from_id(cls, video_id, origin):
        sql = f'''
            insert into video
                (video_id,origin)
            values
                ('{video_id}', '{origin}')
            on conflict (video_id) DO NOTHING;
        '''
        job.execute(sql)
        return job.db.cur.rowcount

    @classmethod
    def bulk_create(cls, video_ids, origin):

        for video_id in video_ids:
            values.append(f"('{video_id}', '{origin}')")

        sql = f''' insert into video (video_id,origin) values {','.join(values)} '''
        job.execute(sql)
        return job.db.cur.rowcount

class Pipeline(Model):

    @classmethod
    def update_status(cls, **kwargs):
        sql = f" update pipeline set status = '{kwargs['status']}' where {kwargs['idname']}= '{kwargs['item_id']}' "
        job.execute(sql)
        return job.db.cur.rowcount

    @classmethod
    def update_lang(cls, **kwargs):
        sql = f" update pipeline set lang = '{kwargs['lang']}', lang_conf = '{kwargs['lang_conf']}' where {kwargs['idname']}= '{kwargs['item_id']}' "
        job.execute(sql)
        return job.db.cur.rowcount

    @classmethod
    def create(cls, **kwargs):
        sql = f'''
                insert into pipeline ({kwargs['idname']}, status)
                values ('{kwargs['item_id']}','incomplete')
                on conflict ({kwargs['idname']}) DO NOTHING;
            '''
        job.execute(sql)
        return job.db.cur.rowcount

class RelatedChannels(object):
     @classmethod
     def insert(cls, **kwargs):
         sql = f'''
                 insert into related_channels (channel_id, related_id, retrieved_at)
                 values ('{kwargs['channel_id']}','{kwargs['related_id']}',NOW())
                 on conflict (channel_id, related_id) DO NOTHING;
             '''
         job.execute(sql)
         return job.db.cur.rowcount


class RecommendedVideos(object):
     @classmethod
     def insert(cls, d):
         sql = f'''
                 insert into video_recommendations
                 (src_video_id, tgt_video_id, harvest_date, tgt_video_harvested_at)
                values ('{d.src_video_id}','{d.tgt_video_id}', '{d.harvest_date}',NOW())
                 on conflict (src_video_id, tgt_video_id, harvest_date) DO NOTHING;
             '''
         job.execute(sql)
         return job.db.cur.rowcount



class VideoScrape(Model):

    @classmethod
    def insert(cls,video_id):
        completed_date = datetime.datetime.now(pytz.timezone('Europe/Amsterdam')).strftime("%Y-%m-%d")
        sql = f'''
                insert into video_scrape (video_id, completed_date, created_at)
                values ('{video_id}', '{completed_date}', now())
                on conflict (video_id) DO NOTHING;
        '''
        job.execute(sql)
        return job.db.cur.rowcount



class Caption(object):
    @classmethod
    def get_lang(cls, url):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        if ('lang' in params.keys()):
            return params['lang'][0]
        else:
            return ''

    @classmethod
    def get_asr(cls, url):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        if ('kind' in params.keys()):
            if (params['kind'][0] == 'asr'):
                return 'b_generated'
            else:
                return 'c_unknown'
        else:
            return 'a_manual'

    @classmethod
    def get_expire(cls, url):
        return urllib.parse.parse_qs(urllib.parse.urlparse(url).query)['expire'][0]

    @classmethod
    def get_captions(cls, caption_urls):
        HTML_TAG_REGEX = re.compile(r'<[^>]*>', re.IGNORECASE)

        captions = []
        for i,u in caption_urls.iterrows():
            http_client = requests.Session()
            result = requests.Session().get(u.url)
            if (result.status_code == 200) and (len(result.text) > 0):

                caption_text = [re.sub(HTML_TAG_REGEX, '', html.unescape(xml_element.text)).replace("\n",' ').replace("\'","'")
                            for xml_element in ElementTree.fromstring(result.text)
                            if xml_element.text is not None
                        ]
                # caption_text = ' '.join(caption_text)
            else:
                caption_text = None

            captions.append({
                'code': result.status_code,
                'len_': len(result.text),
                'expire': datetime.datetime.utcfromtimestamp( int(u.expire)  ).strftime('%Y-%m-%d %H:%M:%S'),
                'text': caption_text,
                'caption_type': u.caption_type,
                'lang': u.lang,
                'caption_url': u.url
            })

        captions = pd.DataFrame(captions)
        return captions


# -------
# class Timer(Model):
#     @classmethod
#     def update_channel_from_feed(cls, d):
#         error = '' if d.ok else ' '.join([str(d.status_code), str(d.empty), str(d.reason)])
#         sql = f''' update timer set
#                     counter = counter +1,
#                     error = $${error}$$,
#                     rss_last_parsing = NOW() ,
#                     rss_next_parsing = NOW() + interval '{d.frequency}'
#                 where channel_id = '{d.channel_id}'
#         '''
#         job.execute(sql)
#         return job.db.cur.rowcount
#
#
#     @classmethod
#     def create(cls, **kwargs):
#         sql = f'''
#                 insert into timer ({kwargs['idname']}, rss_next_parsing)
#                 values ('{kwargs['item_id']}',NOW())
#                 on conflict ({kwargs['idname']}) DO NOTHING;
#             '''
#         job.execute(sql)
#         return job.db.cur.rowcount
