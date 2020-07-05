from .job import *
class Model(object):
    def __init__(self):
        pass

class ChannelStat(Model):

    @classmethod
    def upsert(self,d):
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
