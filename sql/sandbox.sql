-- -----------------------------------------
 SELECT pid, age(clock_timestamp(), query_start), usename, query FROM pg_stat_activity
 WHERE query != '<IDLE>' AND query NOT ILIKE '%pg_stat_activity%' ORDER BY query_start desc;
-- -----------------------------------------
-- -----------------------------------------
 SELECT pid, age(clock_timestamp(), query_start), usename, query FROM pg_stat_activity
 WHERE query = '<IDLE>' AND query NOT ILIKE '%pg_stat_activity%' ORDER BY query_start desc;
-- -----------------------------------------


select v.video_id
from video v
join channel ch on ch.channel_id = v.channel_id
join collection_items ci on ch.channel_id = ci.channel_id
-- left join flow as fl on fl.video_id = v.video_id and fl.flowname = 'video_stats'
left join video_stat vs on (vs.video_id = v.video_id)
where  vs.id is null
   --and fl.id is null
   and ci.collection_id in (15);
