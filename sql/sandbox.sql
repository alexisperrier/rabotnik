update pipeline p
set status = 'foreign'
where p.video_id in (
select v.video_id
    from video v
    join pipeline pc on pc.channel_id = v.channel_id
    join pipeline pv on pv.video_id = v.video_id
    where pc.status = 'foreign'
    and pv.status = 'incomplete'
    order by v.video_id
    limit 10
);

video_id
-------------
001Z9GawEE0
005n4vQidgo
005ts2kUwTo
007yTGOQuW0
00aIKbNQJak
00AkZDbp-ww
00Dh5AZOsS8
0-0-doTRHyQ
00-EqAg3jl0
00EtOR6s_ow

select vv.video_id, ppp.status
from video vv
join pipeline ppp on ppp.video_id = vv.video_id
where vv.video_id in (
    select v.video_id
    from video v
    join pipeline p on p.channel_id = v.channel_id
    join pipeline pp on pp.video_id = v.video_id
    where p.status = 'foreign'
    and pp.status = 'active'
    order by random()
    limit 100
);



select v.video_id, v.published_at, p.status, pch.status, pch.id
from video v
    join pipeline p on p.video_id = v.video_id
    left join pipeline pch on pch.channel_id = v.channel_id
    left join flow as fl on (fl.video_id = v.video_id and fl.flowname = 'complete_videos')
where  v.video_id in (select video_id from pipeline where status = 'incomplete' and video_id is not null order by id desc limit 500)
and p.status = 'incomplete'
and (pch.status = 'active' or pch.id is null)
and fl.id is null
limit 2
offset 2;
