select distinct v.video_id, v.published_at

select count(*)
from video v
left join discussions d on d.video_id = v.video_id
where v.channel_id in (
    select distinct(channel_id)
    from collection_items
    where collection_id in (13, 15, 20,24)
    order by channel_id
    limit 100 offset 100
)
and v.published_at > now() - interval '12 months'
and d.id is null;

--and v.published_at < now() - interval '6 months'


-- liste of videos in collections without captions
0-500:      17k
500-500:    47967
1000-1500:   43032
1500-2000:   30060

select distinct v.channel_id, v.video_id
from video v
left join caption cap on cap.video_id = v.video_id
where v.channel_id in (
    select distinct(channel_id)
    from collection_items
    where collection_id in (13, 15, 20)
    order by channel_id
    limit 500 offset 1500
)
and cap.id is null
order by v.channel_id, v.video_id;

-- and cap.status = 'unavailable'
-- join caption cap on cap.video_id = v.video_id


select distinct v.video_id, v.published_at
from video v
left join discussions d on d.video_id = v.video_id
where v.channel_id in (
    select distinct(channel_id)
    from collection_items
    where collection_id in (13, 15, 20)
    order by channel_id
    limit 200 offset 0
)
and v.published_at > now() - interval '12 months'
and v.published_at < now() - interval '6 months'
and d.id is null
order by v.published_at asc



select count(v.video_id)
from video v
left join discussions d on d.video_id = v.video_id
where v.channel_id in (
    select distinct(channel_id)
    from collection_items
    where collection_id in (13, 15, 20)
)
and v.published_at > now() - interval '6 months'
and v.published_at < now() - interval '7 days'
and d.id is null;


-- # essai de trouver les commentaires par chaine via collection et non par video
-- # tres long
select distinct v.video_id, v.published_at
from video v
left join discussions d on d.video_id = v.video_id
where v.channel_id in (
    select distinct(channel_id)
    from collection_items
    where collection_id in (13, 15, 20)
)
and v.published_at < now() - interval '1 week'
and d.id is null
order by v.published_at asc
limit 200;

UNION
select distinct ci.video_id, v.published_at
from collection_items ci
left join discussions d on d.video_id = ci.video_id
left join flow as fl on (fl.video_id = ci.video_id and fl.flowname = 'video_comments')
join video v on ci.video_id = v.video_id
where v.published_at < now() - interval '60 days'
and fl.id is null
and d.id is null
order by v.published_at asc;




left join flow as fl on (fl.video_id = ci.video_id and fl.flowname = 'video_comments')

select distinct v.video_id, v.published_at
from video v
join collection_items ci on ci.channel_id = v.channel_id
left join discussions d on d.video_id = ci.video_id
where ci.collection_id = 13
and d.id is null;

--and v.published_at < now() - interval '2 days'
-- and fl.id is null
-- left join flow as fl on (fl.video_id = ci.video_id and fl.flowname = 'video_comments')
-- order by v.published_at asc;






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
