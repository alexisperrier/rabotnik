from .flow import *
import datetime
from .text import *
import spacy

class FlowIndexSearch(Flow):

    def __init__(self,**kwargs):
        self.flowname = 'index_search'
        self.max_items  = 100
        super().__init__(**kwargs)
        self.idname     = 'video_id'
        self.operations = ['get_items','freeze','compute','ingest']
        self.nlp = spacy.load("fr_core_news_sm")

    def execution_time(self):   super().execution_time()
    def freeze(self):           super().freeze()
    def get_items(self):        super().get_items()
    def get_sql(self):          super().get_sql()
    def release(self,item_id):  super().release(item_id)
    def update_query(self):     super().update_query()

    def code_sql(self):
        '''
            get the active videos with active channels that are not yet indexed
        '''
        return '''
            select v.video_id, v.title || ' ' || v.summary as text
                from video v
                join pipeline pp on pp.video_id = v.video_id
                left join border b on b.channel_id = v.channel_id
                left join augment au on au.video_id = v.video_id
                left join flow f on f.video_id = v.video_id and f.flowname = 'index_search'
                where b.id is null
                and f.id is null
                and au.id is null
                and (v.summary is not null)
                and pp.status = 'active'
         '''

    def compute(self):
        if (not self.data.empty):
            results = []
            stopwords_rgx = TextUtils.stopwords_rgx()
            self.df = self.data.copy()
            self.df['text'] = self.df.text.apply(lambda txt: stopwords_rgx.sub('', txt) )
            self.df['text'] = self.df.text.apply(lambda txt : TextUtils.lemmatize(self.nlp(txt)))
            self.df['refined_lemma'] = self.df.text.apply(lambda txt :
                    Refine( txt,
                            ['html', 'urls', 'urlswww','punctuation', 'remove_emoji','xao', 'digits']
                        ).text.lower().replace('"',' ')
                )

    def ingest(self):
        for i,d in self.df.iterrows():
            n = IndexSearch.upsert(d)
            # print(d, f"\nn = {n}")
            self.release(d.video_id)


# -----------------
