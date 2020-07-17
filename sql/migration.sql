SELECT  pg_database_size('ytkojo-proddb') ;
11975746051
11954082463
12466426527

select pg_total_relation_size('pipeline');
597901312
604545024

-- drop tables;
drop table channels cascade;
drop table related_videos cascade;
drop table videos cascade;
drop table page cascade;

-- rename video_stat_02 into video_stat
ALTER TABLE video_stat RENAME TO video_stat_01;
ALTER TABLE video_stat_02 RENAME TO video_stat;

-- clone table pipeline

CREATE TABLE backup_pipeline (LIKE pipeline INCLUDING ALL);
INSERT INTO backup_pipeline SELECT * FROM pipeline;

alter table pipeline  drop column blank;
alter table pipeline  drop column complete;
alter table pipeline  drop column video_in_rss;
alter table pipeline  drop column related_videos_counter;
alter table pipeline  drop column queued;
alter table pipeline  drop column api_frequency;

update pipeline set status = 'incomplete' where not channel_complete and channel_id is not null;
update pipeline set status = 'incomplete' where channel_id is not null and status in ('blank')


-- add activity and rss parsing to channel

alter table channel add column activity_score float default 0;
alter table channel add column activity varchar default 'active';
alter table channel add column rss_next_parsing timestamptz default now();

-- import activity score
update channel ch set activity_score = pp.activity_score
from pipeline pp
where ch.channel_id = pp.channel_id and ch.activity_score is distinct from pp.activity_score;

-- import rss_next_parsing
update channel ch set rss_next_parsing = tt.rss_next_parsing
from timer tt
where ch.channel_id = tt.channel_id and ch.rss_next_parsing is distinct from tt.rss_next_parsing

-- activity
update channel ch set activity = pp.status
from pipeline pp
where ch.channel_id = pp.channel_id and ch.activity is distinct from pp.status
and pp.status in ('active','energised','frenetic','sluggish','steady','asleep','cold','dormant');

-- pipeline channel_status
update pipeline set status = 'active' where channel_id is not null and status in ('active','energised','frenetic','sluggish','steady','asleep','dormant','invalid','disabled')
-- status that do not change: feed_error, empty_feed, unavailable
update pipeline set status = 'feed_empty' where channel_id is not null and status in ('empty_feed')
-- maybe reassess all foreign status based on lang and FR (and is has no description look at videos titles and summaries)
update pipeline set status = 'foreign' where channel_id in (
        select channel_id from border where channel_id is not null
    );


alter table pipeline  drop column rss_frequency;
alter table pipeline  drop column activity_score;
alter table pipeline  drop column channel_complete;

-- video and augment
alter table video add column has_tsv boolean default False;
CREATE INDEX video_has_tsv ON video(has_tsv);


update video set has_tsv = True
where video_id in ( select video_id from augment order by id asc limit 200000 offset 200000 );
alter table video  drop column has_tsv;

--
drop timer
drop border



--

-- copy columns between tables
UPDATE table2 t2
SET    val2 = t1.val1
FROM   table1 t1
WHERE  t2.table2_id = t1.table2_id
AND    t2.val2 IS DISTINCT FROM t1.val1;
