select count(*) as n, v.channel_id
from video v
left join channel ch on ch.channel_id = v.channel_id
where ch.id is null
group by v.channel_id
order by n desc
limit 10;
