'''
Gets video comments via YOutube API V3
'''
from .flow import *
from .flow_channel_stats import *
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
        self.parts      = 'snippet,replies'
        self.operations = ['get_items','freeze','query_api','decode', 'ingest_discussions', 'ingest_comments', 'postop', 'bulk_release']


    def code_sql(self):
        '''
            comments only for videos in collections
        '''
        if True:
            return '''
                    select distinct v.video_id, v.published_at
                    from video v
                    left join discussions d on d.video_id = v.video_id
                    left join flow as fl on (fl.video_id = v.video_id and fl.flowname = 'video_comments')
                    where v.channel_id in (
                        select channel_id
                        from collection_items
                        where collection_id in (13, 15, 20,24)
                        and channel_id is not null
                        order by channel_id
                        limit 200 offset 1800
                    )
                    and v.published_at < now() - interval '7 days'
                    and v.published_at > now() - interval '12 months'
                    and d.id is null
                    and fl.id is null
                    order by published_at asc
                    '''
        if False:

            return '''(
                    select distinct v.video_id, v.published_at
                    from video v
                    left join discussions d on d.video_id = v.video_id
                    where v.channel_id in (
                        select distinct(channel_id)
                        from collection_items
                        where collection_id in (13, 15, 20)
                        order by channel_id
                        limit 100 offset 1650
                    )
                    and v.published_at > now() - interval '12 months'
                    and v.published_at < now() - interval '6 months'
                    and d.id is null
                )
                UNION
                    (
                        select distinct ci.video_id, v.published_at
                        from collection_items ci
                        left join discussions d on d.video_id = ci.video_id
                        left join flow as fl on (fl.video_id = ci.video_id and fl.flowname = 'video_comments')
                        join video v on ci.video_id = v.video_id
                        where v.published_at < now() - interval '7 days'
                        and v.published_at > now() - interval '6 months'
                        and fl.id is null
                        and d.id is null
                    )
                    order by published_at asc
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
            print(f"-- {discussion['video_id']} {discussion['total_results']} {discussion['error']}")
            if 'items' in data.keys():
                # df = pd.io.json.json_normalize(data['items']).rename(columns = self.__class__.varnames_api2db)
                df = pd.json_normalize(data['items']).rename(columns = self.__class__.varnames_api2db)
                if not df.empty:
                    replies = []
                    if 'replies.comments' in df.columns:
                        for repcom in df[~df['replies.comments'].isna()]['replies.comments']:
                            for rep in repcom:
                                snippet = rep['snippet']
                                snippet['author_channel_id']= snippet['authorChannelId']['value']
                                snippet['comment_id'] = rep['id']
                                replies.append(snippet)
                        repdf   = pd.DataFrame(replies).rename(columns = self.__class__.varnames_api2db)
                        df = pd.concat([df, repdf], sort=False)[list(set(self.__class__.varnames_api2db.values()))]
                    comments = pd.concat([comments, df], sort=False)


        self.discussions = pd.DataFrame(discussions)
        self.comments   = pd.DataFrame(comments)
        if not self.comments.empty:
            if 'parent_id' in self.comments.columns:
                self.comments.loc[self.comments['parent_id'].isna(), 'parent_id'] = ''
            else:
                self.comments['parent_id'] = ''

            if 'author_name' in self.comments.columns:
                self.comments.loc[self.comments['author_name'].isna(), 'author_name'] = ''
            else:
                self.comments['author_name'] = ''

            if 'author_channel_id' in self.comments.columns:
                self.comments.loc[self.comments['author_channel_id'].isna(), 'author_channel_id'] = ''
            else:
                self.comments['author_channel_id'] = ''

            if 'reply_count' in self.comments.columns:
                self.comments.loc[self.comments['reply_count'].isna(), 'reply_count'] = 0
                self.comments['reply_count'] = self.comments['reply_count'].astype(int)
            else:
                self.comments['reply_count'] = 0

            self.comments['discussion_id'] = ''

    def ingest_discussions(self):
        print(f"== {self.discussions.shape[0]} discussions to insert")
        for i,d in self.discussions.iterrows():
            discussion_id = Discussion.create(d)
            # some comments were found
            if not self.comments.empty:
                cond_comments = self.comments.video_id == d.video_id
                if (not self.comments[cond_comments].empty) and (discussion_id is not None):
                    self.comments.loc[cond_comments, 'discussion_id'] = discussion_id

    def ingest_comments(self):

        n_comments = 0
        print(f"== {self.comments.shape[0]} comments to insert")
        for i,d in self.comments.iterrows():
            n = Comment.create(d)
            n_comments  += n
        print(f"== {n_comments} inserted")


    def postop(self):
        '''
        - all unique channel_ids get stats
        - add video_count to comments: author_video_count
        - if video > 0 and not exist => add to channels
        '''
        if self.comments.empty:
            return None
        print("==" * 20)
        comments_channel_ids = list(self.comments.author_channel_id.unique())
        # comments_channel_ids = list(op.comments.author_channel_id.unique())
        sql = f'''
            select channel_id from channel where channel_id in ('{"','".join(comments_channel_ids)}')
        '''
        existing_channel_ids = pd.read_sql(sql, job.db.conn).channel_id.values
        channel_ids = [id for id in comments_channel_ids if id not in existing_channel_ids]
        print(f" {len(comments_channel_ids)} channels, {len(existing_channel_ids)} exists, {len(channel_ids)} unknown")
        print('--'*20)
        print(channel_ids)
        print('--'*20)

        params = {'flowtag' : False, 'mode' : 'local', 'counting' : False, 'max_items': 50}
        opcs = FlowChannelStats(**params)

        stats = pd.DataFrame()
        start, step = 0,50
        print(f"checking stats for {len(channel_ids)} channels ")
        while start < len(channel_ids) :
            print(f"- {start}/{len(channel_ids)}")
            opcs.item_ids = channel_ids[start: np.min([len(channel_ids), start + 50])]
            opcs.query_api()
            opcs.decode()
            stats = pd.concat([stats, opcs.df])
            start += step

        for c in ['views',  'videos']:
            stats[c] = stats[c].astype(int)

        stats['n'] = stats['views']  + stats['videos']
        stats = stats[(stats.n > 30) & (stats.videos > 2)].reset_index()
        channel_count = 0
        print(f"-- Creating {stats.shape[0]} channels")
        for i,d in stats.iterrows():
            print(f" {d.channel_id} \tv: {d.videos} \ts: {d.subscribers} \tviews: {d.views}  ")
            channel_count += Channel.create(d.channel_id, 'commentators')
            Pipeline.create(idname = 'channel_id',item_id = d.channel_id)
            ChannelStat.upsert(d)
        print(f"-- {channel_count} channels created")


# -----------------
