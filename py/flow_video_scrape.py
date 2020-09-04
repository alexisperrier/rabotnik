'''
Page scraping
'''
from .flow import *
from .text import *
import datetime, time, pytz
import feedparser
import urllib
from xml.etree import ElementTree
import html

class FlowVideoScrape(Flow):

    BASE_URL = 'https://www.youtube.com/watch?v='

    @classmethod
    def validate_page(self, page_html):

        valid_html_exists = page_html is not None

        playability = 'unknown'
        if valid_html_exists:
            start_ = '"playabilityStatus":{'
            end_ = '"}'
            playability = re.findall('{}(.+?){}'.format(start_, end_), page_html)
            valid_playable = not any(["errorScreen" in s for s in playability  ])

            valid_blacklisted = ("Sorry for the interruption" not in page_html) and ("nous excuser pour cette interruption" not in page_html)

        valid = all([valid_html_exists, valid_playable, valid_blacklisted])

        self.ok = valid

        validity = {
            'valid': valid,
            'valid_html_exists': valid_html_exists,
            'valid_playable': valid_playable,
            'valid_blacklisted': valid_blacklisted,
            'playability': playability
        }
        return validity

    # Add video removed detection
    '''
    view-source:https://www.youtube.com/watch?v=03iEgSRppV0
    "playabilityStatus":{"status":"ERROR","reason":"Video unavailable","errorScreen":{"playerErrorMessageRenderer":{"subreason":{"simpleText":"This video is no longer available because the YouTube account associated with this video has been terminated."},"reason":{"simpleText":"Video unavailable"},
    '''


    def __init__(self,**kwargs):
        job.config['offset_factor']     = 0
        self.save_html_file             = False
        self.flowname                   = 'video_scrape'
        self.min_activity_score         = str(0.2)
        self.today                      = datetime.datetime.now(pytz.timezone('Europe/Amsterdam')).strftime("%Y-%m-%d")
        super().__init__(**kwargs)
        self.idname                     = 'video_id'
        self.extra_sleep_time           = 4
        self.min_sleep_time             = 2
        self.operations                 = ['get_items','freeze','request_pages','parse','ingest','parse_captions','postop','availability','bulk_release']


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
                and v.category_id != 20
                and ppch.status = 'active'
                and fl.id is null
                and v.published_at > now() - interval '1 month'
                order by v.published_at desc
         '''

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
            validity = FlowVideoScrape.validate_page(page_html)
            if not validity['valid']:
                invalid_count +=1
            d = {'video_id': video_id,'page_html': page_html}
            d.update(validity)
            data.append(d)

            if self.save_html_file:
                with open(f"./tmp/{video_id}.html", 'w') as f:
                    f.write(page_html)

        self.data = pd.DataFrame(data)

    def parse(self):
        df = []

        for i,d in self.data[self.data.valid].iterrows():
            json_pattern   = list(set(re.findall(r'{"videoId":"[^\"]+"', d.page_html)))
            tgt_video_ids  = list(set([item[12:23] for item in json_pattern if item[12:23] != d.video_id]))
            # extract simpleText
            json_pattern   = list(set(re.findall(r'{"simpleText":"[^\"]+"}', d.page_html)))
            info  = list(set([item[15:] for item in json_pattern]))
            # capture all channelIds as potential recommendation channels and videos

            try:
                channel_ids = [id[12:36] for id in list(set(re.findall(r'channelId":"[^\"]+"', d.page_html)))]
            except:
                channel_ids = []
            print( f"[{d.video_id}] \t tgt_video_ids: {len(tgt_video_ids)} \t {len(channel_ids)} new channels")
            df.append({
                    'channel_ids': channel_ids,
                    'src_video_id'  : d.video_id,
                    'tgt_video_ids'  : tgt_video_ids,
                    'recos_count'   : len(tgt_video_ids),
                    'info'          : ' '.join(info),
                    'tgt_video_harvested_at': datetime.datetime.now(pytz.timezone('Europe/Amsterdam'))
                })

        self.df = pd.DataFrame(df)

    def availability(self):
        for i,d in self.data[~self.data.valid].iterrows():
            sql = f'''
                insert into caption (video_id, status, caption, processed_at)
                values ('{d.video_id}',
                    'unavailable',
                    $${d.playability}$$,
                    now()
                )
                ON CONFLICT (video_id)  DO NOTHING;
            '''
            job.execute(sql)
            res_count = job.db.cur.rowcount
            if not d.valid_playable:
                print(f"-- {d.video_id}: {d.playability}")
                sql = f"update pipeline set status = 'unavailable' where video_id = '{d.video_id}'"
                job.execute(sql)
                sql = f"update video set footer = $${d.playability}$$ where video_id = '{d.video_id}'"
                job.execute(sql)




    def parse_captions(self):
        print("--" * 10," Caption retrieval")
        HTML_TAG_REGEX = re.compile(r'<[^>]*>', re.IGNORECASE)

        start_ = 'https://www.youtube.com/api/timedtext'
        end_ = '",'
        # get caption urls
        self.caption_urls = pd.DataFrame()
        urls = []
        for i,d in self.data[self.data.valid].iterrows():
            m = re.findall('{}(.+?){}'.format(start_, end_), d.page_html)
            if len(m) >0:
                for url in m :
                    urls.append({
                            'video_id': d.video_id,
                            'url': start_+url,
                            'expire': Caption.get_expire(start_+url),
                            'caption_type': Caption.get_asr(start_+url),
                            'lang': Caption.get_lang(start_+url)
                            })

        urls = pd.DataFrame(urls).drop_duplicates()

        self.caption_urls = urls.copy()
        print(f" found {self.caption_urls.shape[0]} caption urls ")

        self.captions = pd.DataFrame()
        captions = []
        for i,u in self.caption_urls.iterrows():
            http_client = requests.Session()
            result = requests.Session().get(u.url)
            if (result.status_code == 200) and (len(result.text) > 0):

                caption_text = [
                    re.sub(HTML_TAG_REGEX, '', html.unescape(xml_element.text)).replace("\n",' ').replace("\'","'")
                            for xml_element in ElementTree.fromstring(result.text)
                            if xml_element.text is not None
                        ]

                captions.append({
                    'video_id': u.video_id,
                    'code': result.status_code,
                    'len_': len(result.text),
                    'expire': datetime.datetime.utcfromtimestamp( int(u.expire)  ).strftime('%Y-%m-%d %H:%M:%S'),
                    'text': caption_text,
                    'caption_type': u.caption_type,
                    'lang': u.lang,
                    'caption_url': u.url
                })

        self.captions = pd.DataFrame(captions)
        if not self.captions.empty:
            self.captions = self.captions[self.captions.lang == 'fr']
        print(f" found {self.captions.shape[0]} French captions ")
        n_captions = 0
        for n,cap in self.captions.iterrows():
            sql = f'''
                insert into caption (video_id, status, caption, wordcount, processed_at, caption_url, caption_type)
                values ('{cap.video_id}',
                    'acquired',
                    $${' '.join(cap.text)}$$,
                    {len(' '.join(cap.text).split())},
                    now() ,
                    '{cap.caption_url}',
                    '{cap.caption_type}'
                )
                ON CONFLICT (video_id)  DO
                UPDATE SET
                    status = 'acquired',
                    caption = $${' '.join(cap.text)}$$,
                    wordcount = {len(' '.join(cap.text).split())},
                    caption_url = '{cap.caption_url}',
                    caption_type = '{cap.caption_type}'
            '''
            job.execute(sql)
            res_count = job.db.cur.rowcount
            if res_count == 0:
                print("--" * 20)
                print(f"[{cap.video_id}] \n{sql}  ")
                print("--" * 20)
            else:
                n_captions += res_count
                print(f"-- caption for {cap.video_id} ")
        print(f"== {n_captions} / {self.data.shape[0]} captions were added ")

    def ingest(self):
        # invalid scrapes
        for i,d in self.data[~self.data.valid].iterrows():
            sql = f'''
                update video_scrape
                set scraped_date = '{self.today}',
                scrape_result = 'failed'
                where video_id = '{d.video_id}'
            '''
            job.execute(sql)

        for i,d in self.df.iterrows():
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
        missing_channel_ids  = [id for id in channel_ids if id not in existing_channel_ids]

        print(f"-- {len(missing_channel_ids)} missing channels: ",missing_channel_ids)
        for channel_id in missing_channel_ids:
            channel_count += Channel.create(channel_id, 'recommended channels')
            Pipeline.create(idname = 'channel_id',item_id = channel_id)

        print(f"-- n_recommended channels added {channel_count}")








# -----------------
