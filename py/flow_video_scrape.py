'''
Page scraping
'''
from .flow import *
from .text import *
import datetime, time, pytz
import feedparser

class FlowVideoScrape(Flow):

    BASE_URL = 'https://www.youtube.com/watch?v='

    @classmethod
    def validate_page(self, page_html):
        valid = (
            (page_html is not None)
            and ("Sorry for the interruption" not in page_html)
            and ("nous excuser pour cette interruption" not in page_html)
        )
        if not valid:
            print(f"page backlisted or empty for video")
        self.ok = valid
        return valid

    def __init__(self,**kwargs):
        self.flowname                   = 'video_scrape'
        self.min_activity_score         = str(0.2)
        self.today                      = datetime.datetime.now(pytz.timezone('Europe/Amsterdam')).strftime("%Y-%m-%d")
        super().__init__(**kwargs)
        self.idname                     = 'video_id'
        self.extra_sleep_time           = 10
        self.min_sleep_time             = 3
        self.operations                 = ['get_items','freeze','request_pages','parse','ingest','postop']

    def code_sql(self):
        '''
            Note: Every new video as a row in video_scrape (see VideoScrape.insert)
            with the scraped_date null by default
        '''
        return '''
            select v.video_id
            from video v
            join pipeline pp on pp.video_id = v.video_id
            join pipeline ppch on ppch.video_id = v.video_id
            join video_scrape vs on (vs.video_id = v.video_id and vs.scraped_date is null)
            left join flow as fl on (fl.video_id = v.video_id and fl.flowname = 'video_scrape')
            where pp.status = 'active'
                and ppch.status = 'active'
                and fl.id is null
         '''

    def tune_sql(self): pass

    def request_pages(self):
        data = []
        invalid_count = 0
        k = 0
        for video_id in self.item_ids:
            sleep_for = np.random.randint( self.min_sleep_time+self.extra_sleep_time )
            time.sleep(sleep_for)
            http_client = requests.Session()
            text        = http_client.get(FlowVideoScrape.BASE_URL + video_id).text
            page_html   = text.replace('\\u0026', '&').replace('\\', '')
            print(f"-- [{k}/{self.max_items}] {video_id}  len: {len(page_html)}")
            k +=1
            if not FlowVideoScrape.validate_page(page_html):
                invalid_count +=1

            data.append({'video_id': video_id, 'valid': FlowVideoScrape.validate_page(page_html), 'page_html': page_html})
            if False:
                with open(f"./tmp/{video_id}.html", 'w') as f:
                    f.write(page_html)

            self.data = pd.DataFrame(data)

    def parse(self):
        df = []

        for i,d in self.data[self.data.valid].iterrows():
            json_pattern   = list(set(re.findall(r'{"videoId":"[^\"]+"', d.page_html)))
            tgt_video_ids  = list(set([item[12:23] for item in json_pattern if item[12:23] != d.video_id]))
            print( f"[{d.video_id}] tgt_video_ids: {len(tgt_video_ids)} ")
            # extract simpleText
            json_pattern   = list(set(re.findall(r'{"simpleText":"[^\"]+"}', d.page_html)))
            info  = list(set([item[15:] for item in json_pattern]))
            # capture all channelIds as potential recommendation channels and videos

            try:
                # channel_id = list(set(re.findall(r'externalChannelId":"[^\"]+"', d.page_html)))[0][20:44]
                channel_ids = [id[12:36] for id in list(set(re.findall(r'channelId":"[^\"]+"', d.page_html)))]
            except:
                channel_ids = []
            print(f"-- found {len(channel_ids)} channel_ids: {channel_ids}")
            df.append({
                    'channel_ids': channel_ids,
                    'src_video_id'  : d.video_id,
                    'tgt_video_ids'  : tgt_video_ids,
                    'recos_count'   : len(tgt_video_ids),
                    'info'          : ' '.join(info),
                    'tgt_video_harvested_at': datetime.datetime.now(pytz.timezone('Europe/Amsterdam'))
                })

        self.df = pd.DataFrame(df)

    def ingest(self):
        # invalid scrapes
        for i,d in self.data[~self.data.valid].iterrows():
            sql = '''
                update video_scrape
                set scraped_date = '{self.today}'
                scrape_result = 'failed'
                where video_id = '{d.src_video_id}'
            '''
            job.execute(sql)

        for i,d in self.df.iterrows():
            self.release(d.src_video_id)
            sql = f'''
                update video_scrape
                set scraped_date = '{self.today}' ,
                    scrape_result = 'ok',
                    recos_count = {d.recos_count}
                where video_id = '{d.src_video_id}'
            '''
            job.execute(sql)
            if (len(d.tgt_video_ids) > 0):
                values = []
                for tgt_video_id in d.tgt_video_ids:
                    values.append(f"('{d.src_video_id}', '{tgt_video_id}', '{self.today}', '{d.tgt_video_harvested_at}' )")

                sql = f''' insert into video_recommendations
                    (src_video_id, tgt_video_id, harvest_date, tgt_video_harvested_at)
                    values {','.join(values)}
                    on conflict (src_video_id,tgt_video_id,harvest_date) DO NOTHING;
                '''
                job.execute(sql)
                ni  = job.db.cur.rowcount

    def postop(self):
        if self.df.empty:
            return None

        n = 0
        tgt_video_ids = []
        for i,d in self.df.iterrows():
            tgt_video_ids += d.tgt_video_ids
        tgt_video_ids = list(set(tgt_video_ids))

        sql = f'''
            select video_id from video where video_id in ('{"','".join(tgt_video_ids)}')
        '''
        existing_video_ids = pd.read_sql(sql, job.db.conn).video_id.values
        missing_video_ids  = [id for id in tgt_video_ids if id not in existing_video_ids]
        print(f"-- {len(missing_video_ids)}  missing_videos: ",missing_video_ids)
        if len(missing_video_ids) > 0:
            for video_id in missing_video_ids:
                n += Video.create_from_id(video_id, "recommended videos")
                Pipeline.create(idname = 'video_id',item_id = video_id)

        # create channel_id if not exists
        print("--"*5, "recommended channel creation")
        channel_count = 0
        channel_ids = []
        for i,d in self.df.iterrows():
            channel_ids += d.channel_ids

        sql = f'''
            select channel_id, title from channel where channel_id in ('{"','".join(channel_ids)}')
        '''
        existing_channel_ids = pd.read_sql(sql, job.db.conn).channel_id.values
        missing_channel_ids = [id for id in channel_ids if id not in existing_channel_ids]

        print(f"-- {len(missing_channel_ids)} missing channels: ",missing_channel_ids)
        for channel_id in missing_channel_ids:
            channel_count += Channel.create(channel_id, 'recommended channels')
            Pipeline.create(idname = 'channel_id',item_id = channel_id)

        print(f"-- n_recommended channels added {channel_count}")








# -----------------
