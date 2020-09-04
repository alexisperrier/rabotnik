from .flow import *
import datetime

class FlowVideoComments(Flow):

    varnames_api2db = {
        'id': 'comment_id',
        'snippet.videoId': 'video_id',
        'snippet.topLevelComment.snippet.textOriginal': "text",
        'snippet.topLevelComment.snippet.textDisplay': "text_html",
        'snippet.topLevelComment.snippet.authorDisplayName': "author_name",
        'snippet.topLevelComment.snippet.authorChannelId.value': "author_channel_id",
        'snippet.topLevelComment.snippet.likeCount': 'like_count',
        'snippet.topLevelComment.snippet.publishedAt': 'published_at',
        'snippet.totalReplyCount': 'reply_count',
        'videoId': 'video_id',
        'textOriginal': 'text',
        'textDisplay': 'text_html',
        'parentId': 'parent_id',
        'authorDisplayName': "author_name",
        'authorChannelId.value': "author_channel_id",
        'likeCount': 'like_count',
        'publishedAt': 'published_at',
    }

    def __init__(self,**kwargs):
        self.flowname = 'video_comments'
        super().__init__(**kwargs)
        self.endpoint   = 'commentThreads'
        self.idname     = 'video_id'
        # self.max_items  = 1
        self.parts      = 'snippet,replies'
        self.operations = ['get_items','freeze','query_api','decode', 'ingest', 'bulk_release']


    def code_sql(self):
        return '''
            select video_id from video order by random() limit 10
         '''

    def query_api(self):
        self.content = []
        self.status_code = []
        self.ok          = []
        self.reason      = []
        for video_id in self.item_ids:
            self.video_id   = video_id
            results         = APIrequest(self,job).get()
            self.content.append(json.loads(results.result.content.decode('utf-8')))
            self.status_code.append(results.result.status_code)
            self.ok.append(results.result.ok)
            self.reason.append(results.result.reason)

    def decode(self):
        discussions = []
        comments = pd.DataFrame()
        for video_id, data in zip(self.item_ids, self.content):
        # for video_id, data in zip(op.item_ids, op.content):

            if 'error' in data.keys():
                try:
                    reason = data['error']['errors'][0]['reason']
                except:
                    reason = ''
                try:
                    error_message = data['error']['message']
                except:
                    error_message = ''


                discussion = {
                    'video_id': video_id,
                    'total_results': 0,
                    'results_per_page': 0,
                    'error': ' '.join([reason, error_message])
                }
            else:
                discussion = {
                    'video_id': video_id,
                    'total_results': data['pageInfo']['totalResults'],
                    'results_per_page': data['pageInfo']['resultsPerPage'],
                    'error': ''
                }

            discussions.append(discussion)
            print(discussion)
            if 'items' in data.keys():
                df = pd.io.json.json_normalize(data['items']).rename(columns = self.__class__.varnames_api2db)
                if not df.empty:
                    replies = []
                    if 'replies.comments' in df.columns:
                        for repcom in df[~df['replies.comments'].isna()]['replies.comments']:
                            for rep in repcom:
                                snippet = rep['snippet']
                                snippet['authorChannelId']= snippet['authorChannelId']['value']
                                snippet['comment_id'] = rep['id']
                                replies.append(snippet)
                        repdf   = pd.DataFrame(replies).rename(columns = self.__class__.varnames_api2db)
                        df = pd.concat([df, repdf], sort=False)[list(set(self.__class__.varnames_api2db.values()))]
                    comments = pd.concat([comments, df], sort=False)


        self.discussions = pd.DataFrame(discussions)
        print(self.discussions)
        self.comments   = pd.DataFrame(comments)
        if not self.comments.empty:
            self.comments.loc[self.comments['parent_id'].isna(), 'parent_id'] = ''
            self.comments.loc[self.comments['author_name'].isna(), 'author_name'] = ''
            self.comments.loc[self.comments['author_channel_id'].isna(), 'author_channel_id'] = ''
            self.comments.loc[self.comments['reply_count'].isna(), 'reply_count'] = 0
            self.comments['reply_count'] = self.comments['reply_count'].astype(int)


    def ingest(self):
        print(f"== {self.discussions.shape[0]} discussions to insert")
        for i,d in self.discussions.iterrows():
            discussion_id = Discussion.create(d)
            if not self.comments.empty:
                if d.video_id in self.comments.video_id.unique():
                    self.comments.loc[self.comments.video_id == d.video_id, 'discussion_id'] = discussion_id

        if not self.comments.empty:
            self.comments['discussion_id'] = self.comments['discussion_id'].astype(int)
        n_comments = 0
        print(f"== {self.comments.shape[0]} comments to insert")
        for i,d in self.comments.iterrows():
            n = Comment.create(d)
            n_comments  += n
        print(f"== {n_comments} inserted")





# -----------------
