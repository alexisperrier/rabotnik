from .flow import *
import datetime
from .text import *
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
# import numpy as np

class FlowChannelTopics(Flow):

    def __init__(self,**kwargs):
        self.flowname = 'channel_topics'
        self.max_items  = 50
        super().__init__(**kwargs)
        self.idname     = 'channel_id'
        self.operations = ['get_items','freeze','compute','ingest']
        self.nlp = spacy.load("fr_core_news_sm")

    def code_sql(self):
        return '''
            select ch.channel_id
            from channel ch
            left join flow f on f.channel_id = ch.channel_id and f.flowname = 'channel_topics'
            left join topic tc on tc.channel_id = ch.channel_id
            where ch.activity_score > 0.4
            and ((tc.id is null) or (tc.created_at < now() - interval '1 month') )
            and f.id is null
            order by ch.activity_score desc
         '''

    def compute(self):

        results = []
        stopwords_rgx = TextUtils.stopwords_rgx()
        for channel_id in self.item_ids:
            topics = None
            print("--"*10,"\n", "channel_id",channel_id)
            sql = f'''
                select v.video_id, v.title, v.summary, ch.title,
                (select max(views) from video_stat vs where vs.video_id = v.video_id ) as views,
                v.title || ' ' || v.summary || ' ' || coalesce(cap.caption,'') as raw_text
                from video v
                join channel ch on ch.channel_id = v.channel_id
                left join caption cap on v.video_id = cap.video_id
                where v.channel_id = '{channel_id}'
                and v.published_at > now() - interval '1 month'
                and ((cap.status = 'acquired') or (cap.status is null))
                order by v.pubdate desc
                limit 500
            '''

            df = pd.read_sql(sql, job.db.conn).sort_values(by = 'views', ascending = False).reset_index(drop = True)

            if ~df.empty and (df.shape[0] > 5):
                if df.shape[0] > 50:
                    df = df[:50].reset_index(drop = True)

                df['text']  = df.raw_text.apply(lambda txt: stopwords_rgx.sub('', txt) )
                # lemmatize
                df['text'] = df.text.apply(lambda txt : TextUtils.lemmatize(self.nlp(txt)))
                df['text'] = df.text.apply(lambda txt :
                        Refine( txt,
                                ['html', 'urls', 'urlswww','punctuation', 'remove_emoji','xao', 'digits']
                            ).text.lower().replace('"',' ')
                    )

                corpus = list(set(df.text.values))
                n_components = np.min( [int(len(corpus) / 3), 10])
                if n_components > 1:
                    tfidf_vectorizer = TfidfVectorizer(
                            max_df          = 0.5,
                            min_df          = 0,
                            max_features    = 2000,
                            strip_accents   = 'ascii',
                            stop_words      = ["'"],
                            ngram_range     = (1,1),
                        )
                    dtm_tfidf = tfidf_vectorizer.fit_transform(corpus)
                    lda_tfidf = LatentDirichletAllocation(n_components=n_components, random_state=0)
                    lda_tfidf.fit(dtm_tfidf)
                    tf_feature_names = tfidf_vectorizer.get_feature_names()
                    n_top_words = 15
                    topics = {}
                    for topic_idx, topic in enumerate(lda_tfidf.components_):
                        topics[topic_idx] =  " ".join([tf_feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]])
                    topics = json.dumps(topics)
                    print(topics)
            results.append({'channel_id': channel_id, 'topics': topics})

        self.df = pd.DataFrame(results)

    def ingest(self):
        for i,d in self.df.iterrows():
            ChannelTopic.upsert(d)
            # self.release(d.channel_id)


# -----------------
