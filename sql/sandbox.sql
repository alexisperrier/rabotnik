-- some queries

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
