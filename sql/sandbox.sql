select v.video_id
from video v
join pipeline p on p.video_id = v.video_id
join pipeline pch on pch.channel_id = v.channel_id
join channel ch on ch.channel_id = v.channel_id
left join flow as fl on fl.video_id = v.video_id and fl.flowname = 'video_stats'
left join video_stat vs on ( (vs.video_id = v.video_id) and (vs.viewed_at > '2020-07-31'))
where v.pubdate in ('2020-07-25','2020-07-17','2020-07-02','2020-06-02')
and pch.status = 'active'
and ch.activity in ('energised','frenetic')
and v.category_id != 20
and fl.id is null
and vs.id is null
and p.status = 'active';
