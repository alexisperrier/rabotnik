select count(*) as n
-- , v.category_id, cat.category
from video v
-- left join yt_categories cat on cat.category_id = v.category_id
join pipeline p on p.video_id = v.video_id
left join flow as fl on fl.video_id = v.video_id and fl.flowname = 'video_stats'
left join video_stat vs on ( (vs.video_id = v.video_id) and (vs.viewed_at > '{timespan_01}'))
where v.pubdate in ('{timespan_02}')
   --and v.category_id != 20
   and fl.id is null
   and vs.id is null
   and p.status = 'active'
   -- group by v.category_id, cat.category
   order by n;


   select count(*) as n
   , v.category_id, cat.category
   from video v
   left join yt_categories cat on cat.category_id = v.category_id
join pipeline p on p.video_id = v.video_id
left join flow as fl on fl.video_id = v.video_id and fl.flowname = 'video_stats'
left join video_stat vs on ( (vs.video_id = v.video_id) and (vs.viewed_at > '2020-07-26'))
where v.pubdate in ('2020-07-26','2020-07-25','2020-07-24','2020-07-23','2020-07-22','2020-07-21','2020-07-20','2020-07-13','2020-07-06','2020-06-29','2020-05-28')
and v.category_id != 20
and fl.id is null
and vs.id is null
and p.status = 'active'
group by v.category_id, cat.category
order by n;



select * from video v
join pipeline p on p.video_id = v.video_id
where p.status = 'incomplete'
and p.video_id is not null
and v.summary is null
order by v.id desc
limit 10;

select count(*) as n, v.origin
from video v
join pipeline p on p.video_id = v.video_id
where p.status = 'incomplete'
and p.video_id is not null
and v.channel_id is not null
group by v.origin order by n;
order by v.id desc
limit 10;



select count(*) as n
from video v
    join pipeline p on p.video_id = v.video_id
    left join pipeline pch on pch.channel_id = v.channel_id
    left join flow as fl on (fl.video_id = v.video_id and fl.flowname = 'complete_videos')
where  v.video_id in (select video_id from pipeline
            where status = 'incomplete' and video_id is not null
        )
and p.status = 'incomplete'
and (pch.status = 'active' or pch.id is null)
and fl.id is null;



select count(*) as n, v.category_id, cat.category
from video v
join yt_categories cat on cat.category_id = v.category_id
join pipeline pp on pp.video_id = v.video_id
join pipeline ppch on ppch.video_id = v.video_id
join video_scrape vs on (vs.video_id = v.video_id and vs.scraped_date is null)
left join flow as fl on (fl.video_id = v.video_id and fl.flowname = 'video_scrape')
where pp.status = 'active'
    and v.category_id != 20
    and ppch.status = 'active'
    and fl.id is null
    group by v.category_id, cat.category
    order by n;
