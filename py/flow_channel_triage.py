'''
Channel Triage
'''
from .flow import *
from .text import *
import datetime, time
import feedparser
from .flow_feed_parsing import FlowFeedParsing

class FlowChannelTriage(Flow):

    BASE_URL = 'https://www.youtube.com/feeds/videos.xml?channel_id='
    varnames_feed2db = {
        'published': 'published_at',
        'published_parsed': 'published_parsed',
    }

    def __init__(self,**kwargs):
        self.flowname = 'channel_triage'
        super().__init__(**kwargs)
        self.idname = 'channel_id'
        self.operations = ['get_items','parse','ingest']

    def tune_sql(self):         pass

    def code_sql(self):
        return '''
            select p.channel_id
            from pipeline p
            where p.status = 'incomplete'
            and lang is null
            and channel_id is not null
            order by random()
         '''

    def parse(self):
        ld = LangDetector()
        channels = []
        sql = f''' select channel_id, collection_id from collection_items  where channel_id in ('{"','".join(self.item_ids)}')  '''
        self.collections = pd.read_sql(sql, job.db.conn)
        print(f"self.collections {self.collections}")


        for channel_id in self.item_ids:
            result    = feedparser.parse( FlowFeedParsing.BASE_URL +  channel_id )

            if (result.status == 200) & (len(result.entries) > 0):
                channel_title = result['feed']['title'].lower()
                texts = [ entry['title'].lower() for entry in result.entries] + [result['feed']['title'].lower()]
                lang_predicted = ld.predict(  ' '.join(texts).replace("\n",' '))
                lang_conf = lang_predicted['conf']
                lang = lang_predicted['lang']
                if (lang_predicted['lang'] == 'fr') & (lang_conf > 0.4):
                    channel_status = 'incomplete'
                    lang = 'fr'
                else:
                    channel_status = 'foreign'
                    if lang_conf < 0.2:
                        lang = '--'

                # estimate activity
                # entries = pd.io.json.json_normalize(result.entries)[FlowChannelTriage.varnames_feed2db.keys()]
                entries = pd.json_normalize(result.entries)[FlowChannelTriage.varnames_feed2db.keys()]
                entries.rename(columns = FlowChannelTriage.varnames_feed2db, inplace = True)
                entries['in_collection'] = channel_id in self.collections.channel_id.unique()
                entries.sort_values(by = 'published_at', ascending = False, inplace = True)
                entries.reset_index(inplace = True, drop = True)
                frequency, activity, activity_score = FlowFeedParsing.activity_score(entries)

                # if the channel is valid (FR), then next rss parsing should happen soon
                if channel_status == 'incomplete':
                    frequency = '2 hours'

            elif (result.status == 200) & (len(result.entries) == 0):
                print("empty feed")
                frequency, activity, activity_score, channel_status = '60 days', None, None, 'feed_empty'
                lang, lang_conf = '--', 0.0
                channel_title = '--'
                texts = []
            else:
                print("feed error", result.status, result.bozo)
                frequency, activity, activity_score, channel_status = '4 week', None, None, 'feed_error'
                lang, lang_conf = '--', 0.0
                channel_title = '--'
                texts = []


            print(f"[{channel_id}] {frequency}, {activity}, {activity_score}, {channel_status} {lang} {lang_conf}")
            channels.append({
                'channel_id' : channel_id,
                'title': channel_title,
                'channel_status'  : channel_status,
                'texts': ' '.join(texts),
                'lang': lang,
                'lang_conf': lang_conf,
                'frequency'  : frequency,
                'activity'  : activity,
                'activity_score'  : activity_score,
            })

        self.channels = pd.DataFrame(channels)
        print(self.channels.channel_status.value_counts())
        print(self.channels.lang.value_counts())

    def ingest(self):

        for i,d in self.channels.iterrows():
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
                    title       = $${TextUtils.to_db(d.title)}$$,
                    {str_activity}
                    {str_activity_score}
                    rss_next_parsing = NOW() + interval '{d.frequency}',
                    retrieved_at = now()
                where channel_id = '{d.channel_id}'
            '''
            # print(sql)
            job.execute(sql)

            sql = f''' update pipeline
                set lang = '{d.lang}',
                lang_conf = '{d.lang_conf}',
                status = '{d.channel_status}'
                where channel_id = '{d.channel_id}' '''
            job.execute(sql)
            # print(sql)







# -----------------
