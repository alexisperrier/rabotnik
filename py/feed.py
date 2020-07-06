import feedparser
import datetime
import time

class YtFeed(object):

    BASE_URL = 'https://www.youtube.com/feeds/videos.xml?channel_id='

    def __init__(self,channel_id):
        self.channel_id = channel_id

    def parse(self):
        result    = feedparser.parse( YtFeed.BASE_URL +  self.channel_id )
        self.status_code = result.status
        self.ok          = (result.status == 200) & (len(result.entries) > 0)
        self.reason      = result.bozo
        self.content     = result


    def channel_status_frequency_activity(self):
        '''
            interval between most recent and oldest video in feed / 2
            or if most recent video is old => arbitrary long interval
        '''
        publication_dates = [c['published'] for c in self.content.entries]
        recent  =  time.mktime(parser.parse( publication_dates[0] ).timetuple())
        oldest  =  time.mktime(parser.parse( publication_dates[-1] ).timetuple())
        now     =  time.mktime(datetime.datetime.now().timetuple())

        n_days          = max(1,  int((now - oldest) / (3600*24)))
        n_videos        = len(self.content.entries)
        activity_score  = np.round( n_videos / n_days, 2)

        # 6 months since last video
        if (now - recent) > 15552000:
            print("6 months since last video")
            frequency = '90 days'
            channel_status = 'dormant'
        # 90 days since last video
        elif (now - recent) > 7776000:
            print("90 days since last video")
            frequency = '15 days'
            channel_status = 'asleep'
        # one week since last video => depends on activity_score
        else:
            if activity_score <= 0.1:
                channel_status  = 'sluggish'
                frequency       = '3 days'
            elif activity_score <= 0.5:
                channel_status  = 'steady'
                frequency       = '1 day'
            elif activity_score <= 1:
                channel_status  = 'active'
                frequency       = '12 hours'
            elif activity_score <= 5:
                channel_status  = 'energised'
                frequency       = '6 hours'
            else: # more than 5 videos per day
                channel_status  = 'frenetic'
                frequency       = '2 hours'

        self.rss_frequency  = frequency
        self.channel_status = channel_status
        self.activity_score = activity_score
        self.api_frequency  = Channel.API_FREQUENCY[channel_status]
