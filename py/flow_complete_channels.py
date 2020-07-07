'''
see https://developers.google.com/youtube/v3/docs/channels#resource
'''
from .flow import *
import datetime
import isodate
from .text import *
import distutils.util

class FlowCompleteChannels(Flow):

    varnames_api2db = {
        'id': 'channel_id',
        'snippet.publishedAt': 'created_at',
        'snippet.title': 'title',
        'snippet.description': 'description',
        'snippet.thumbnails.default.url':'thumbnail',
        'snippet.customUrl': 'custom_url',
        'snippet.country': 'country',
        'brandingSettings.channel.showRelatedChannels': 'show_related',
        'brandingSettings.channel.featuredChannelsUrls': 'related_channel_ids'
    }

    def __init__(self,**kwargs):
        self.flowname = 'complete_channels'
        super().__init__(**kwargs)
        self.endpoint   = 'channels'
        self.idname     = 'channel_id'
        self.parts      = 'snippet,brandingSettings'
        snippet_str     = 'title,description,publishedAt,customUrl,thumbnails/default/url,country'
        self.fields     = f"items(id,snippet({snippet_str}),brandingSettings(channel/showRelatedChannels,channel/featuredChannelsUrls))"
        self.related_channel_ids = []
        self.channel_growth = False
        if self.channel_growth:
            self.operations.append('postop')



    def prune(self):            super().prune()
    def execution_time(self):   super().execution_time()
    def freeze(self):           super().freeze()
    def get_items(self):        super().get_items()
    def get_sql(self):          super().get_sql()
    def query_api(self):        super().query_api()
    def release(self,item_id):  super().release(item_id)
    def update_query(self):     super().update_query()

    def code_sql(self):
        return '''
            select ch.channel_id
            from channel ch
                join pipeline p on p.channel_id = ch.channel_id
                left join border b on b.channel_id = ch.channel_id
                left join flow as fl on fl.channel_id = ch.channel_id
            where p.channel_id is not null
                and not p.channel_complete
                and p.status in ('active','energised','frenetic','sluggish','steady','asleep','cold','dormant','blank')
                and b.id is null
                and fl.id is null
            order by ch.id asc
         '''

    def decode(self):
        super().decode()
        if (not self.df.empty):
            for col in ['custom_url','country']:
                if col in self.df.columns:
                    self.df.loc[self.df[col].isna(), col] = ''
                else:
                    self.df[col] = ''

            self.df.loc[ self.df.show_related.isna(), 'show_related']  = ''
            self.df['title']        = self.df.title.apply(lambda d : TextUtils.valid_string_db(d) )
            self.df['description']  = self.df.description.apply(lambda d : TextUtils.valid_string_db(d) )

    def ingest(self):
        print(f"== {self.df.shape} to insert")
        for i,d in self.df.iterrows():
            # print(d.channel_id)
            Channel.update(d)
            Pipeline.update_status(idname = 'channel_id',  item_id = d.channel_id, status = 'active')
            sql = f"update pipeline set channel_complete = True where channel_id = '{d.channel_id}'"
            job.execute(sql)
            self.release(d.channel_id)

        # related channels
        if 'related_channel_ids' in self.df.columns:
            data = self.df[~self.df['related_channel_ids'].isna()]
            print(f"{data.shape[0]} channels have related channels")
            for i,d in data.iterrows():
                for related_id in d.related_channel_ids:
                    RelatedChannels.insert(channel_id = d.channel_id, related_id = related_id)
                    self.related_channel_ids.append(related_id)
        else:
            print("no related channels")


    def tune_sql(self):
        pass

    def postop(self):
        print(f"insert {len(self.related_channel_ids)} related channels")
        for channel_id in self.related_channel_ids:
            Channel.create(channel_id, 'related channels')
            Pipeline.create(idname = 'channel_id',item_id = channel_id)
            Timer.create(idname = 'channel_id',item_id = channel_id)





# -----------------
