update pipeline
set status = 'active'
where channel_id in (
    select ch.channel_id from channel ch
    join pipeline p on p.channel_id = ch.channel_id
    where p.status = 'foreign'
    and (ch.country = 'FR')
    limit 100
);

= ch.channel_id
    and p.status = 'foreign'
    and (ch.country == 'FR');


select v.video_id, v.published_at, p.status, pch.status, pch.id
from video v
    join pipeline p on p.video_id = v.video_id
    left join pipeline pch on pch.channel_id = v.channel_id
    left join flow as fl on (fl.video_id = v.video_id and fl.flowname = 'complete_videos')
where  v.video_id in (select video_id from pipeline where status = 'incomplete' and video_id is not null order by id desc limit 500)
and p.status = 'incomplete'
and (pch.status = 'active' or pch.id is null)
and fl.id is null;
