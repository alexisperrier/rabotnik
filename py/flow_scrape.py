'''
Page scraping
'''
from .flow import *
from .text import *
import datetime, time, pytz
import feedparser

class FlowScrape(Flow):

    BASE_URL = 'https://www.youtube.com/watch?v='

    @classmethod
    def validate_page(self, page_html):
        valid = (
            (page_html is not None)
            and ("Sorry for the interruption" not in page_html)
            and ("nous excuser pour cette interruption" not in page_html)
        )
        if not valid:
            print(f"page backlisted or empty for video {sef.video_id}")
        self.ok = valid
        return valid


    def __init__(self,**kwargs):
        self.flowname                   = 'scrape'
        self.published_since_interval   = '4 weeks'
        self.min_activity_score         = str(0.2)
        self.today                      = datetime.datetime.now(pytz.timezone('Europe/Amsterdam')).strftime("%Y-%m-%d")
        self.max_items                  = 20
        super().__init__(**kwargs)
        self.idname                     = 'video_id'
        self.extra_sleep_time           = 4
        self.min_sleep_time             = 2
        self.operations                 = ['get_items','freeze','request_pages','parse','ingest','postop']

    def execution_time(self):   super().execution_time()
    def freeze(self):           super().freeze()
    def get_items(self):        super().get_items()
    def get_sql(self):          super().get_sql()
    def release(self,item_id):  super().release(item_id)
    def update_query(self):     super().update_query()

    def code_sql(self):
        return '''
             select v.video_id
             from video v
             join pipeline pp on pp.video_id = v.video_id
             join pipeline ppch on ppch.channel_id = v.channel_id
             left join video_recommendations vr on (vr.src_video_id = v.video_id and vr.harvest_date = '{today}')
             left join border b on b.channel_id = v.channel_id
             left join flow as fl on (fl.video_id = v.video_id and fl.flowname = 'scrape')
             where v.pubdate is not null
                 and v.published_at > now() - interval '{published_since_interval}'
                 and pp.status = 'active'
                 and ppch.status in ('frenetic','energised','steady','active')
                 and ppch.activity_score > 0.20
                 and ( (pp.lang = 'fr') or (pp.lang is not null))
                 and vr.id is null
                 and b.id is null
                 and fl.id is null
         '''

    def tune_sql(self):
        self.sql = self.sql.replace(
                '{published_since_interval}', self.published_since_interval
            ).replace(
                '{min_activity_score}', self.min_activity_score
            ).replace(
                '{today}', self.today
            )

    def request_pages(self):
        data = []
        invalid_count = 0
        for video_id in self.item_ids:
            sleep_for = np.random.randint( self.min_sleep_time+self.extra_sleep_time )
            time.sleep(sleep_for)
            http_client = requests.Session()
            text        = http_client.get(FlowScrape.BASE_URL + video_id).text
            page_html   = text.replace('\\u0026', '&').replace('\\', '')
            print(f"{video_id}  len: {len(page_html)}")
            if not FlowScrape.validate_page(page_html):
                invalid_count +=1

            data.append({'video_id': video_id, 'valid': FlowScrape.validate_page(page_html), 'page_html': page_html})

            if invalid_count > 2:
                self.ok = False
                break;
            self.data = pd.DataFrame(data)

    def parse(self):
        df = []

        for i,d in self.data[self.data.valid].iterrows():
            link_pattern    = list(set(re.findall(r'href="/watch[^\"]+"', d.page_html)))
            video_01 = [item[15:26] for item in link_pattern if item[15:26] != d.video_id]

            json_pattern   = list(set(re.findall(r'{"videoId":"[^\"]+"', d.page_html)))
            video_02   = [item[12:23] for item in json_pattern if item[12:23] != d.video_id]
            print( f"[{d.video_id}] url pattern : {len(video_01)} json pattern: {len(video_02)} ")

            for tgt_video_id in list(set(video_01 + video_02)):
                df.append({'src_video_id': d.video_id,
                    'tgt_video_id':tgt_video_id,
                    'harvest_date': self.today,
                    'tgt_video_harvested_at': datetime.datetime.now(pytz.timezone('Europe/Amsterdam'))
                    })
        self.df = pd.DataFrame(df)

    def ingest(self):
        n = 0
        print(f"self.df.shape {self.df.shape[0]}")
        for i,d in self.df.iterrows():
            n += RecommendedVideos.insert(d)
            self.release(d.src_video_id)
        print(f"-- {n} video recommendations added ")

    def postop(self):
        n = 0
        tgt_video_ids = self.df.tgt_video_id.values
        sql = f'''
            select video_id from video where video_id in ('{"','".join(tgt_video_ids)}')
        '''
        existing_video_ids = pd.read_sql(sql, job.db.conn).video_id.values
        missing_video_ids = [id for id in tgt_video_ids if id not in existing_video_ids]
        print("missing_video_ids",missing_video_ids)
        for video_id in missing_video_ids:
            n += Video.create_from_id(video_id, "recommended videos")
            Pipeline.create(idname = 'video_id',item_id = video_id)
            Timer.create(   idname = 'video_id',item_id = video_id)

        print(f"-- n_recommended videos added {n}")




# -----------------
