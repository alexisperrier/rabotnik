select v.video_id
from video v
join pipeline pp on pp.video_id = v.video_id
join channel ch on ch.channel_id = v.channel_id
join video_scrape vs on (vs.video_id = v.video_id and vs.scraped_date is null)
left join flow as fl on (fl.video_id = v.video_id and fl.flowname = 'video_scrape')
where pp.status = 'active'
    and ch.activity in ('frenetic','energised','steady','active')
    -- and ch.activity_score > {min_activity_score}
    --and ch.activity_score > 0.2
    and fl.id is null


select v.video_id
from video v
join pipeline pp on pp.video_id = v.video_id
join pipeline ppch on ppch.video_id = v.video_id
join video_scrape vs on (vs.video_id = v.video_id and vs.scraped_date is null)
left join flow as fl on (fl.video_id = v.video_id and fl.flowname = 'video_scrape')
where pp.status = 'active'
    and ppch.status = 'active'
    and fl.id is null
