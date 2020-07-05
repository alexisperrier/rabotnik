import requests

class APIkey(object):

    @classmethod
    def count(self):
        # TODO: if n == 0: raise alert
        job.execute("select count(*) from apikeys where status = 'active'")
        n = job.db.cur.fetchone()[0]
        return n

    def __init__(self,job):
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
        Execute request to the API
    '''

    def __init__(self,flow,job) -> None:
        self.base_url   = 'https://www.googleapis.com/youtube/v3/'
        self.url        = self.base_url + flow.endpoint

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
