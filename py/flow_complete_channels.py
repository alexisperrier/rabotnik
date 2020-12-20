'''
Gets channel data from Youtube API
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
        # self.max_items = 2
        super().__init__(**kwargs)
        self.endpoint   = 'channels'
        self.idname     = 'channel_id'
        self.parts      = 'snippet,brandingSettings'
        snippet_str     = 'title,description,publishedAt,customUrl,thumbnails/default/url,country'
        self.fields     = f"items(id,snippet({snippet_str}),brandingSettings(channel/showRelatedChannels,channel/featuredChannelsUrls))"
        self.related_channel_ids = []
        if job.channel_growth:
            self.operations.append('postop')

    def tune_sql(self): pass

    def code_sql(self):
        return '''
            select ch.channel_id
            from channel ch
            join pipeline p on p.channel_id = ch.channel_id
            left join flow as fl on fl.channel_id = ch.channel_id and fl.flowname = 'complete_channels'
            where p.status = 'incomplete'
                and fl.id is null
                and p.lang is not null
            order by ch.id asc
         '''

    def decode(self):
        super().decode()
        ld = LangDetector()
        if (not self.df.empty):
            for col in ['custom_url','country']:
                if col in self.df.columns:
                    self.df.loc[self.df[col].isna(), col] = ''
                else:
                    self.df[col] = ''

            self.df['lang_predicted'] = self.df.apply(lambda d : ld.predict(  ' '.join([d.title,d.description]).replace("\n",' ')) , axis = 1)
            self.df['lang_conf'] = self.df.lang_predicted.apply(lambda d : d['conf'])
            self.df['lang'] = self.df.lang_predicted.apply(lambda d : d['lang'])

            self.df.loc[ self.df.show_related.isna(), 'show_related']  = ''
            self.df['title']        = self.df.title.apply(lambda d : TextUtils.to_db(d) )
            self.df['description']  = self.df.description.apply(lambda d : TextUtils.to_db(d) )


    def ingest(self):
        print(f"== {self.df.shape} to update")
        for i,d in self.df.iterrows():
            print(d.channel_id)
            Channel.update(d)
            Pipeline.update_status(idname = 'channel_id',  item_id = d.channel_id, status = 'active')
            Pipeline.update_lang(idname = 'channel_id',  item_id = d.channel_id, lang = d.lang, lang_conf = d.lang_conf)
            # self.release(d.channel_id)

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


    def postop(self):
        print(f"creating {len(self.related_channel_ids)} related channels if not exists")
        channel_count = 0
        for channel_id in self.related_channel_ids:
            channel_count += Channel.create(channel_id, 'related channels')
            Pipeline.create(idname = 'channel_id',item_id = channel_id)
        print(f"{channel_count} related channels created")





# -----------------
