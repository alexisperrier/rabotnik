select v.video_id, v.published_at, p.status, pch.status, pch.id
from video v
    join pipeline p on p.video_id = v.video_id
    left join pipeline pch on pch.channel_id = v.channel_id
    left join flow as fl on (fl.video_id = v.video_id and fl.flowname = 'complete_videos')
where p.status = 'incomplete'
and (pch.status = 'active' or pch.id is null)
and fl.id is null
order by random() limit 10;


select v.video_id, v.published_at, p.status, pch.status, pch.id
from video v
    join pipeline p on p.video_id = v.video_id
    left join pipeline pch on pch.channel_id = v.channel_id
    left join flow as fl on (fl.video_id = v.video_id and fl.flowname = 'complete_videos')
where p.status = 'incomplete'
and (pch.status = 'active' or pch.id is null)
and fl.id is null
