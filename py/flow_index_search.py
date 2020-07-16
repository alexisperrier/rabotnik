from .flow import *
import datetime
from .text import *
import spacy
import timeout_decorator

class FlowIndexSearch(Flow):

    def __init__(self,**kwargs):
        self.flowname = 'index_search'
        self.max_items  = 100
        super().__init__(**kwargs)
        self.idname     = 'video_id'
        self.operations = ['get_items','freeze','compute','ingest']
        self.nlp = spacy.load("fr_core_news_sm")

    def code_sql(self):
        '''
            get the active videos with active channels that are not yet indexed
            only the videos published within the last month otherwise query takes too long
        '''
        return '''
            select v.video_id, v.title || ' ' || v.summary as text
                from video v
                join pipeline pp on pp.video_id = v.video_id
                left join augment au on au.video_id = v.video_id
                left join flow f on f.video_id = v.video_id and f.flowname = 'index_search'
                where  v.published_at > now() - interval '1 months'
                and pp.status = 'active'
                and (v.summary is not null)
                and au.id is null
                and f.id is null
         '''

    @timeout_decorator.timeout(180)
    def compute(self):
        if (not self.data.empty):
            results = []
            stopwords_rgx = TextUtils.stopwords_rgx()
            self.df = self.data[:min([self.max_items, self.data.shape[0]])].copy()
            self.df['text'] = self.df.text.apply(lambda txt: stopwords_rgx.sub('', txt) )
            self.df['text'] = self.df.text.apply(lambda txt :
                    Refine( txt,
                            ['html', 'urls', 'urlswww','punctuation', 'remove_emoji','xao', 'digits']
                        ).text.lower().replace('"',' ')
                )
            self.df['refined_lemma'] = self.df.text.apply(lambda txt : TextUtils.lemmatize(self.nlp(txt)))

    def ingest(self):
        for i,d in self.df.iterrows():
            n = IndexSearch.upsert(d)
            self.release(d.video_id)


# -----------------
