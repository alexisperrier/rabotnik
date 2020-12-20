-- some queries 

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
