import requests
import datetime

class APIkey(object):
    '''
        Handles Youtube API keys:
        - init: gets an active from the database
        - count: how many active keys
        - standby: puts a key in standby mode
    '''

    @classmethod
    def count(self):
        # TODO: if n == 0: raise alert
        job.execute("select count(*) from apikeys where status = 'active'")
        n = job.db.cur.fetchone()[0]
        return n

    def __init__(self,job):
        '''
        Youtube API keys are stored in the database
        '''
        sql = '''
            select apikey from apikeys where status = 'active'
            order by random()
            limit 1;
        '''
        job.db.cur.execute(sql)
        self.apikey = job.db.cur.fetchone()[0]

    def standby(self):
        '''
        Sets the status of apikey to standby
        '''
        sql = f'''
            update apikeys
            set status  = 'standby',
            standby_at  = NOW()
            where apikey = '{self.apikey}'
        '''
        job.execute(sql)


class APIrequest(object):
    '''
        Execute requests to the API
    '''

    def __init__(self,flow,job) -> None:
        '''
        - builds params with info from the instanciated fLow
        - sets API endpoint URL
        '''
        self.base_url   = 'https://www.googleapis.com/youtube/v3/'
        self.url        = self.base_url + flow.endpoint

        if flow.endpoint == "search":
            published_after = (datetime.datetime.now() - datetime.timedelta(days = flow.since_days)).strftime('%Y-%m-%dT%H:%M:%SZ')

            self.request_params = {
                'key':                  job.apikey,
                'part':                 flow.parts,
                'fields':               flow.fields,
                'maxResults':           50,
                'order':                'date',
                'safeSearch':           'none',
                'type':                 'video',
                'regionCode':           'FR',
                'publishedAfter':       published_after,
                'relevanceLanguage':    'fr',
                'q':                    flow.keyword
            }


        elif flow.endpoint == "commentThreads":

            self.request_params = {
                'key':      job.apikey,
                'video_id':       flow.video_id,
                'part':     flow.parts,
                'maxResults': 100,
                'moderationStatus': 'published',
                'order': 'relevance'
            }
        else:
            self.request_params = {
                'key':      job.apikey,
                'id':       ','.join(flow.item_ids),
                'part':     flow.parts,
                'fields':   flow.fields
            }

    def get(self):
        '''
            returns request result
        '''
        self.result =  requests.get(self.url,self.request_params)

        return self




# --
