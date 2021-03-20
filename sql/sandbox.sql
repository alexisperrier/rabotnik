-- some queries
select count(v.id) as n, v.pubdate
from video v
join pipeline p on p.video_id = v.video_id
where p.status = 'active'
and v.pubdate > '2020-05-01'
and  v.pubdate < '2021-01-01'
group by pubdate;


select v.video_id, c.*
from video v
left join comments c  on c.video_id = v.video_id
where v.channel_id in (
    select distinct(channel_id)
    from collection_items
    where collection_id in (24)
    order by channel_id
    limit 100
)
and v.published_at > '2020-12-01' limit 10;
