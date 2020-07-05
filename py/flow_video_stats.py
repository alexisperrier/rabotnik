from .flow import *

class FlowVideoStats(Flow):

    varnames_api2db = {
        'id': 'video_id',
        'statistics.viewCount': "views"
    }

    def __init__(self,**kwargs):
        self.flowname = 'video_stats'
        super().__init__(**kwargs)
        self.max_items  = 2
        self.endpoint   = 'videos'
        self.idname     = 'video_id'
        self.parts      = 'statistics'
        self.fields     = 'items(id,statistics(viewCount))'
