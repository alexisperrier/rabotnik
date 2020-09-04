1ci05SiZrDM
3rY77MwvzhY

insert into flow (video_id, flowname, mode, start_at) values ('3rY77MwvzhY', 'complete_videos','forced', now());
insert into flow (video_id, flowname, mode, start_at) values ('1ci05SiZrDM', 'complete_videos','forced', now());

insert into flow (video_id, flowname, mode, start_at) values ('9P9dpFGhD1M', 'complete_videos','forced', now());
insert into flow (video_id, flowname, mode, start_at) values ('8i5KIUFZI00', 'complete_videos','forced', now());

-- complete videos
select col.video_id, p.*, v.origin, v.retrieved_at
-- select col.video_id
from collection_items col
join pipeline p on p.video_id = col.video_id
join video v on v.video_id = col.video_id
where v.duration is null
and p.status != 'unavailable'
order by p.status, col.video_id
limit 2;

-- complete video_stat
select col.video_id, p.*
from collection_items col
join pipeline p on p.video_id = col.video_id
left join video_stat vs on vs.video_id = col.video_id
where vs.video_id is null
and p.status != 'unavailable'
order by p.status limit 2;


-- caption
select col.video_id, p.*, cap.status, cap.wordcount, cap.processed_at
from collection_items col
join pipeline p on p.video_id = col.video_id
left join caption cap on cap.video_id = col.video_id
where ((cap.video_id is null) or (cap.status = 'queued'))
and p.status != 'unavailable'
order by p.status limit 2;


-- video_recommendations
select col.video_id, p.*
from collection_items col
join pipeline p on p.video_id = col.video_id
left join video_recommendations vr on vr.src_video_id = col.video_id
where vr.src_video_id is null
and p.status != 'unavailable'
order by p.status limit 2;

insert into flow (video_id, flowname, mode, start_at) values ('Go0GEMOOZus', 'video_stats','forced', now());


insert into flow (video_id, flowname, mode, start_at) values ('015SPE4raAY', 'video_scrape','forced', now());

insert into flow (video_id, flowname, mode, start_at) values ('03iEgSRppV0', 'video_scrape','forced', now());


-- complete_channels

select ch.channel_id
from channel ch
join video v on v.channel_id = ch.channel_id
where v.video_id in (select distinct video_id from collection_items)
and ch.title is null
limit 100;

select ch.channel_id
from channel ch
join video v on v.channel_id = ch.channel_id
where ch.title is null
and v.video_id in (select distinct video_id from collection_items)
limit 100;

select ch.channel_id, p.status
from channel ch
join pipeline p on p.channel_id = ch.channel_id
where ch.title is null
limit 100;


select ch.channel_id
from video v
join channel ch on v.channel_id = ch.channel_id
where v.video_id in (select distinct video_id from collection_items)
and ch.title is null
limit 100;
