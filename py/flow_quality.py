# from .flow import *
#
# class FlowQuality(Flow):
#
#     def __init__(self,**kwargs):
#         self.flowname   = 'quality'
#         kwargs['mode']  = 'local'
#         kwargs['counting']  = True
#         job.config['offset_factor'] = 0
#         super().__init__(**kwargs)
#         self.max_items = 2
#         self.operations = ['quality']
#         self.tasks = ['complete_videos','complete_channels','video_scrape','video_stats']
#
#
#     def code_sql(self): pass
#
#     def quality(self):
#         for task in self.tasks:
#             idname, qsql = getattr(self, f"sql_{task}")()
#             data = pd.read_sql(qsql, job.db.conn)
#             print(f"- {task}: \t{data.shape} rows")
#             for i, d in data.iterrows():
#                 sql = f''' insert into flow ({idname}, flowname, mode, start_at)
#                     values ('{d[idname]}', '{task}','forced', now())
#                     on conflict ({idname}, flowname) DO NOTHING
#                  '''
#                 job.execute(sql)
#
#     def sql_complete_videos(self):
#         return  'video_id',f'''
#             select col.video_id
#             from collection_items col
#             join pipeline p on p.video_id = col.video_id
#             join video v on v.video_id = col.video_id
#             where v.duration is null
#             and p.status != 'unavailable'
#             order by col.video_id limit {self.max_items}
#         '''
#
#     def sql_complete_channels(self):
#         return 'channel_id',f'''
#             select ch.channel_id
#             from channel ch
#             join video v on v.channel_id = ch.channel_id
#             where ch.title is null
#             and v.video_id in (select distinct video_id from collection_items)
#             order by ch.channel_id limit {self.max_items}
#         '''
#
#     def sql_video_stats(self):
#         return 'video_id',f'''
#             select col.video_id
#             from collection_items col
#             join pipeline p on p.video_id = col.video_id
#             left join video_stat vs on vs.video_id = col.video_id
#             where vs.video_id is null
#             and p.status != 'unavailable'
#             order by col.video_id limit {self.max_items}
#         '''
#
#     def sql_video_scrape(self):
#         return 'video_id',f'''
#             select col.video_id
#             from collection_items col
#             join pipeline p on p.video_id = col.video_id
#             left join video_recommendations vr on vr.src_video_id = col.video_id
#             where vr.src_video_id is null
#             and p.status != 'unavailable'
#             order by col.video_id limit {self.max_items}
#         '''




# -----------------
