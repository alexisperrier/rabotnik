-- psql create database ytkojo_proddb;
-- psql -U postgres ytkojo_proddb  -f sql/create_ytkojo.sql

-- ---------------------------------------------------------------------
--  channel
-- ---------------------------------------------------------------------
drop table if exists channel;
create table channel (
    id serial NOT NULL,
    channel_id varchar(24),
    title varchar,
    description varchar,
    country varchar,
    custom_url varchar,
    thumbnail varchar,
    origin varchar,
    complete boolean default False,
    has_related boolean default False,
    created_at timestamptz,
    retrieved_at timestamptz
);

CREATE UNIQUE INDEX unique_channel_id ON channel(channel_id);

CREATE INDEX channel_origin ON channel(origin);

-- ---------------------------------------------------------------------
--  video
-- ---------------------------------------------------------------------
drop table if exists video;
create table video (
    id serial NOT NULL,
    video_id char(11),
    channel_id char(24),
    title varchar,
    summary varchar,
    thumbnail varchar,
    category_id int,
    tags varchar,
    duration varchar,
    privacy_status varchar,
    caption BOOLEAN default False,
    origin varchar,
    published_at timestamptz,
    retrieved_at timestamptz
);
ALTER TABLE video ALTER COLUMN "tags" varchar;
ALTER TABLE video RENAME COLUMN tags TO tmp;
ALTER TABLE video ADD COLUMN tags varchar;
ALTER TABLE video ADD COLUMN origin varchar;
ALTER TABLE video ADD COLUMN footer varchar;

ALTER TABLE video ADD pubdate char(10)


CREATE UNIQUE INDEX unique_video_id ON video(video_id);
CREATE INDEX idx_video_channel_id ON video(channel_id);
CREATE INDEX video_origin ON video(origin);
CREATE INDEX video_published_at ON video(published_at);

drop table if exists pipeline;
create table pipeline (
    id serial NOT NULL,
    video_id char(11),
    channel_id char(24),
    lang varchar(10),
    lang_conf float default Null,
    status varchar default 'incomplete',
    blank BOOLEAN default True,
    complete BOOLEAN default False,
    video_in_rss BOOLEAN default True,
    rss_frequency varchar default '1 day',
    api_frequency varchar default '1 day',
    activity_score  float default 0,
    channel_complete boolean default False,
    related_videos_counter int default 0,
    created_at timestamptz default now()
);
CREATE UNIQUE INDEX unique_piepline_channel_id ON pipeline(channel_id);
ALTER TABLE pipeline  ADD COLUMN lang_conf float default Null;
ALTER TABLE pipeline  ALTER COLUMN lang varchar(10);
ALTER TABLE pipeline  ALTER COLUMN status set default 'incomplete';

ALTER TABLE pipeline  ADD COLUMN activity_score float default 0;
ALTER TABLE pipeline  ADD COLUMN channel_complete boolean default False;
ALTER TABLE pipeline  ADD COLUMN related_videos_counter int default 0;

CREATE UNIQUE INDEX unique_pipeline_video_id ON pipeline(video_id);
ALTER TABLE pipeline  ADD COLUMN queued boolean default False;


drop table if exists timer;

create table timer (
    id serial NOT NULL,
    video_id char(11),
    channel_id char(24),
    error varchar default NULL,
    counter integer default 0,
    rss_last_parsing timestamptz,
    rss_next_parsing timestamptz,
    api_last_request timestamptz,
    api_next_request timestamptz
);

CREATE UNIQUE INDEX unique_timer_video_id ON timer(video_id);
CREATE UNIQUE INDEX unique_timer_channel_id ON timer(channel_id);

drop table if exists related_channels;
create table related_channels (
    id serial NOT NULL,
    channel_id varchar,
    related_id varchar,
    retrieved_at timestamptz default NOW()
);

CREATE UNIQUE INDEX unique_related_channel_id ON related_channels(channel_id, related_id);


drop table if exists related_videos;
create table related_videos (
    id serial NOT NULL,
    src_video_id varchar,
    tgt_video_id varchar,
    tgt_channel_id varchar default NULL,
    tgt_channel_title varchar default NULL,
    tgt_video_lang varchar default NULL,
    position int,
    request_counter int default 0,
    tgt_published_at timestamptz default NULL,
    tgt_channel_exists boolean,
    tgt_video_exists boolean,
    retrieved_at timestamptz default NOW()
);


-- ----------------------------------------------
--  Experiment tables
-- ----------------------------------------------
drop table if exists exp_related_videos_01;
create table exp_related_videos_01 (
    id serial NOT NULL,
    source_id int,
    src_channel_id varchar,
    src_video_id varchar,
    src_video_title varchar,
    position int,
    tgt_channel_id varchar default NULL,
    tgt_channel_title varchar default NULL,
    tgt_channel_exists boolean,
    tgt_video_lang varchar default NULL,
    tgt_video_id varchar,
    tgt_video_published_at timestamptz default NULL,
    tgt_video_exists   boolean,
    tgt_video_title    varchar default NULL,
    retrieved_at timestamptz default NOW(),
    processed varchar default 'new',
    harvest_date date
);

-- ALTER TABLE exp_related_videos_01 ADD COLUMN harvest_date date;

drop type  if exists  apikey_status CASCADE;
CREATE TYPE apikey_status AS ENUM ('active','standby','invalid');

drop table if exists apikeys ;
create table apikeys (
    id serial NOT NULL,
    apikey varchar,
    status apikey_status default 'active',
    email varchar,
    standby_at timestamptz  default NULL,
    created_at timestamptz  default NOW()
);


drop type  if exists  caption_status CASCADE;
CREATE TYPE caption_status AS ENUM ('acquired','unavailable','queued');

drop table if exists caption ;
create table caption (
    id serial NOT NULL,
    video_id char(11),
    status caption_status default 'queued',
    caption varchar default NULL,
    wordcount int default NULL,
    processed_at timestamptz default NULL
);
ALTER TABLE caption ADD COLUMN caption_url varchar default Null;
ALTER TABLE caption ADD COLUMN caption_type varchar default Null;
ALTER TYPE caption_status ADD VALUE 'error'

CREATE UNIQUE INDEX unique_caption_id ON caption(video_id);

drop type  if exists  page_status CASCADE;
CREATE TYPE page_status AS ENUM ('queued','acquired','unavailable','error');

drop table if exists page ;
create table page (
    id serial NOT NULL,
    video_id char(11),
    status page_status default 'queued',
    retrieved_at timestamptz default NULL
);


drop table if exists video_stat;
create table video_stat(
    id serial Not Null,
    video_id varchar Not Null,
    view_count int,
    source varchar default 'rss',
    retrieved_at timestamptz
);

ALTER TABLE video_stat ADD COLUMN eod boolean default False;

-- alter table video_stat RENAME TO video_stat_01;
drop table if exists video_stat_02;
create table video_stat_02(
    id serial Not Null,
    video_id char(11),
    source char(3) default 'rss',
    views int default 0,
    viewed_at char(10) not null
);

CREATE UNIQUE INDEX unique_video_stat ON video_stat_02(video_id, viewed_at);


drop table if exists channel_stat;
create table channel_stat(
    id serial Not Null,
    channel_id char(24) not null,
    views int default 0,
    subscribers int default 0,
    videos int default 0,
    retrieved_at timestamptz
);

ALTER TABLE channel_stat  ALTER COLUMN views TYPE bigint;

CREATE UNIQUE INDEX channel_stat_channel_id ON channel_stat(channel_id);

drop table if exists flow;
create table flow(
    id serial Not Null,
    channel_id char(24),
    video_id char(11),
    flowname varchar not null,
    start_at timestamptz
);

CREATE UNIQUE INDEX unique_video_flow ON flow(video_id, flowname);
CREATE UNIQUE INDEX unique_channel_flow ON flow(channel_id, flowname);
ALTER TABLE flow ADD COLUMN  mode varchar default 'organic';

drop table if exists query;
create table query(
    id serial Not Null,
    sql varchar  not null,
    queryname varchar not null,
    created_at timestamptz default now()
);

ALTER TABLE query ADD COLUMN active boolean default true;

CREATE UNIQUE INDEX unique_queryname ON query(queryname);


drop table if exists yt_categories;
create table yt_categories(
    id serial Not Null,
    category_id int  not null,
    category varchar  not null,
    assignable boolean
);

drop table if exists plot ;
create table plot (
    id serial NOT NULL,
    image_id varchar,
    location varchar,
    plottype varchar,
    plotparams json,
    error varchar,
    generated_at timestamptz not null default now()
);

CREATE UNIQUE INDEX unique_image_id ON plot(image_id);

-- ---------------------------------------------------------------------
--  recommended / related videos 2020 may 2nd
-- ---------------------------------------------------------------------

drop table if exists related_videos_02;
create table related_videos_02 (
    id serial NOT NULL,
    harvest_date            varchar,
    status                  varchar,
    -- source channels and videos
    src_channel_id          char(24),
    src_video_id            char(11),
    src_video_status        varchar default null,
    -- recommended video
    tgt_video_id            char(11),
    -- status in pipeline, null is video not exists
    tgt_video_status        varchar default null,
    tgt_video_harvested_at  timestamptz,
    -- to be completed later from db or API
    tgt_channel_id          char(24),
    tgt_channel_title       varchar default NULL,
    tgt_video_lang          varchar default NULL,
    tgt_video_title         varchar default NULL,
    tgt_video_published_at  timestamptz default NULL
);

CREATE INDEX channel_related_videos_02 ON related_videos_02(src_channel_id);
CREATE INDEX harvest_date_related_videos_02 ON related_videos_02(harvest_date);
CREATE INDEX video_related_videos_02 ON related_videos_02(src_video_id);

create index unique_related_videos_02 on related_videos_02(src_video_id, harvest_date, tgt_video_id, status);



-- ---------------------------------------------------------------------
--  video recommendations 2020 May 15th
-- ---------------------------------------------------------------------

drop table if exists video_recommendations;
create table video_recommendations (
    id serial NOT NULL,
    src_video_id            char(11),
    tgt_video_id            char(11),
    harvest_date            varchar,
    tgt_video_harvested_at  timestamptz
);

CREATE INDEX src_video_video_recommendations ON video_recommendations(src_video_id);
CREATE INDEX tgt_video_video_recommendations ON video_recommendations(tgt_video_id);
CREATE UNIQUE INDEX unique_vid_recommendation_src_tgt_date_id ON video_recommendations(src_video_id, tgt_video_id, harvest_date);
-- ---------------------------------------------------------------------
--  out of bounds: oobounds 2020 May 18th
-- ---------------------------------------------------------------------

drop table if exists border;
create table border (
    id serial NOT NULL,
    video_id            char(11),
    channel_id            char(24),
    created_at  timestamptz default now()
);

CREATE UNIQUE INDEX border_channel ON border(channel_id);
CREATE UNIQUE INDEX border_video ON border(video_id);


-- ---------------------------------------------------------------------
--  video augmented info 2020 May 30th
-- ---------------------------------------------------------------------

drop table if exists augment;
create table augment (
    id          serial NOT NULL,
    video_id    char(11),
    tsv         tsvector,
    tsv_lemma         tsvector,
    created_at  timestamptz default now()
);

CREATE UNIQUE INDEX augment_video_id ON augment(video_id);

CREATE INDEX augment_tsv_idx ON augment USING gin(tsv);
CREATE INDEX augment_tsv_lemma_idx ON augment USING gin(tsv_lemma);

-- ---------------------------------------------------------------------
--  jobqueue
-- ---------------------------------------------------------------------

drop table if exists helm ;
create table helm  (
    id          serial NOT NULL,
    jobname     varchar not null,
    count_      int default 0 not null,
    created_at  timestamptz default now()
);

CREATE INDEX helm_jobname ON helm(jobname) ;


-- ---------------------------------------------------------------------
--  exports
-- ---------------------------------------------------------------------

drop table if exists export ;
create table export  (
    id          serial NOT NULL,
    location     varchar not null,
    generated_at  timestamptz default now()
);


-- ---------------------------------------------------------------------
--  topic
-- ---------------------------------------------------------------------

drop table if exists topic ;
create table topic  (
    id          serial NOT NULL,
    channel_id  char(24),
    topics json,
    created_at  timestamptz default now()
);

CREATE UNIQUE INDEX topic_channel_id ON topic(channel_id);


-- ---------------------------------------------------------------------
--  video_scrape
-- ---------------------------------------------------------------------
drop table if exists video_scrape ;
create table video_scrape  (
    id          serial NOT NULL,
    video_id  char(11),
    completed_date char(10) default null,
    scraped_date char(10) default null,
    scrape_result varchar default null,
    downloaded_date char(10) default null,
    recos_count int default null,
    captions varchar default null,
    created_at  timestamptz default now()
);

CREATE UNIQUE INDEX video_scrape_id ON video_scrape(video_id);

-- ---------------------------------------------------------------------
--  channel_origin
-- ---------------------------------------------------------------------
drop table if exists origin ;
create table origin  (
    id          serial NOT NULL,
    channel_id  char(24),
    origin      varchar default null,
    filename    varchar default null,
    created_at  timestamptz default now()
);

CREATE UNIQUE INDEX origin_channel_id ON origin(origin,channel_id);





-- --
