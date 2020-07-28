select count(*) as n, pch.status
from video v
join pipeline p on p.video_id = v.video_id
join pipeline pch on p.channel_id = v.channel_id
left join flow as fl on fl.video_id = v.video_id and fl.flowname = 'video_stats'
left join video_stat vs on ( (vs.video_id = v.video_id) and (vs.viewed_at > '2020-07-27'))
where v.pubdate in ('2020-07-27','2020-07-26','2020-07-25','2020-07-24','2020-07-23','2020-07-22','2020-07-21','2020-07-14','2020-07-07','2020-06-30','2020-05-29')
   -- and pch.status = 'active'
   --and v.category_id != 20
   and fl.id is null
   and vs.id is null
   and p.status = 'active'
   group by pch.status;
