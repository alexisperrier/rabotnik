-- list of command line to dump the database from Google SQl
-- and load it into a local postgres db

exports
export_items
pg_stat_statements
active_storage_blobs
active_storage_attachments

pg_dump -h 127.0.0.1 -p 3307 -U postgres --format plain --verbose --file exports.sql --table public.exports ytkojo-proddb
pg_dump -h 127.0.0.1 -p 3307 -U postgres --format plain --verbose --file export_items.sql --table public.export_items ytkojo-proddb
pg_dump -h 127.0.0.1 -p 3307 -U postgres --format plain --verbose --file apikeys.sql --table public.apikeys ytkojo-proddb
pg_dump -h 127.0.0.1 -p 3307 -U postgres --format plain --verbose --file users.sql --table public.users ytkojo-proddb
pg_dump -h 127.0.0.1 -p 3307 -U postgres --format plain --verbose --file collections.sql --table public.collections ytkojo-proddb
pg_dump -h 127.0.0.1 -p 3307 -U postgres --format plain --verbose --file schema_migrations.sql --table public.schema_migrations ytkojo-proddb
pg_dump -h 127.0.0.1 -p 3307 -U postgres --format plain --verbose --file query.sql --table public.query ytkojo-proddb
pg_dump -h 127.0.0.1 -p 3307 -U postgres --format plain --verbose --file searches.sql --table public.searches ytkojo-proddb
pg_dump -h 127.0.0.1 -p 3307 -U postgres --format plain --verbose --file helm.sql --schema-only --table public.helm ytkojo-proddb
pg_dump -h 127.0.0.1 -p 3307 -U postgres --format plain --verbose --file flow.sql --schema-only --table public.flow ytkojo-proddb

psql -U postgres -d ytkojodb -1 -f yt_categories.sql
psql -U postgres -d ytkojodb -1 -f exports.sql
psql -U postgres -d ytkojodb -1 -f export_items.sql
psql -U postgres -d ytkojodb -1 -f apikeys.sql
psql -U postgres -d ytkojodb -1 -f users.sql
psql -U postgres -d ytkojodb -1 -f collections.sql
psql -U postgres -d ytkojodb -1 -f schema_migrations.sql
psql -U postgres -d ytkojodb -1 -f query.sql
psql -U postgres -d ytkojodb -1 -f searches.sql
psql -U postgres -d ytkojodb -1 -f helm.sql
psql -U postgres -d ytkojodb -1 -f flow.sql


-- take  2 larger tables

--topic                      |   23453696
pg_dump -h 127.0.0.1 -p 3307 -U postgres --format plain --verbose --file topic.sql --table public.topic ytkojo-proddb
psql -U postgres -d ytkojodb -1 -f topic.sql

-- collection_items           |   25976832
pg_dump -h 127.0.0.1 -p 3307 -U postgres --format plain --verbose --file collection_items.sql --table public.collection_items ytkojo-proddb
psql -U postgres -d ytkojodb -1 -f collection_items.sql

-- discussions                |   41041920
pg_dump -h 127.0.0.1 -p 3307 -U postgres --format plain --verbose --file discussions.sql --table public.discussions ytkojo-proddb
psql -U postgres -d ytkojodb -1 -f discussions.sql


-- related_channels           |   54484992
pg_dump -h 127.0.0.1 -p 3307 -U postgres --format plain --verbose --file related_channels.sql --table public.related_channels ytkojo-proddb
psql -U postgres -d ytkojodb -1 -f related_channels.sql


-- channel_stat               |   58990592
pg_dump -h 127.0.0.1 -p 3307 -U postgres --format plain --verbose --file channel_stat.sql --table public.channel_stat ytkojo-proddb
psql -U postgres -d ytkojodb -1 -f channel_stat.sql


--  video_scrape                    |  403660800
pg_dump -h 127.0.0.1 -p 3307 -U postgres --format plain --verbose --file video_scrape.sql --table public.video_scrape ytkojo-proddb
psql -U postgres -d ytkojodb -1 -f video_scrape.sql

--  channel                    |  377970688
pg_dump -h 127.0.0.1 -p 3307 -U postgres --inserts --format plain --verbose --file channel.sql --table public.channel ytkojo-proddb
psql -U postgres -d ytkojodb -1 -q -f channel.sql


--  caption                    |  614375424
[done]  pg_dump -h 127.0.0.1 -p 3307 -U postgres --inserts --no-owner --format plain --verbose --file caption.sql --table public.caption ytkojo-proddb
[done] psql -U postgres -d ytkojodb -1 -q -f caption.sql


-- pipeline                   |  979542016
[done]  pg_dump -h 127.0.0.1 -p 3307 -U postgres --inserts  --no-owner --format plain --verbose --file pipeline.sql --table public.pipeline ytkojo-proddb
[done] psql -U postgres -d ytkojodb -1 -q -f pipeline.sql


-- video_recommendations      | 1741258752
[done]  pg_dump -h 127.0.0.1 -p 3307 -U postgres --no-owner --format plain --verbose --file video_recommendations.sql --table public.video_recommendations ytkojo-proddb
[done] psql -U postgres -d ytkojodb -1 -q -f video_recommendations.sql

-- augment                    | 1997570048
[done] pg_dump -h 127.0.0.1 -p 3307 -U postgres --no-owner --format plain --verbose --file augment.sql --table public.augment ytkojo-proddb
[done] psql -U postgres -d ytkojodb -1 -q -f augment.sql

-- comments                   | 3990929408
[done] pg_dump -h 127.0.0.1 -p 3307 -U postgres --inserts  --no-owner --format plain --verbose --file comments.sql --table public.comments ytkojo-proddb
[done] psql -U postgres -d ytkojodb -1 -q -f comments.sql


-- video                      | 6693543936
[done] pg_dump -h 127.0.0.1 -p 3307 -U postgres --inserts  --no-owner --format plain --verbose --file video.sql --table public.video ytkojo-proddb
[done] psql -U postgres -d ytkojodb -1 -q -f video.sql

-- video_stat                 | 6780289024
[todo] pg_dump -h 127.0.0.1 -p 3307 -U postgres  --no-owner --format plain --verbose --file video_stat.sql --table public.video_stat ytkojo-proddb
[todo] psql -U postgres -d ytkojodb -1 -q -f video_stat.sql


dns = f'''
    dbname=ytkojodb
    user=postgres
    host=127.0.0.1
    password=
'''
conn = psycopg2.connect(dbname="ytkojodb", user="postgres", host="127.0.0.1", password="hello")
cur  = conn.cursor()



--
table_name         | table_size
----------------------------+------------
exports                    |          0
export_items               |          0
pg_stat_statements         |          0
User                       |          0
active_storage_blobs       |          0
active_storage_attachments |          0
ar_internal_metadata       |       8192
apikeys                    |       8192
yt_categories              |       8192
users                      |       8192
collections                |       8192
schema_migrations          |       8192
query                      |      24576
searches                   |      24576
helm                       |     229376
flow                       |    1122304
topic                      |   23453696
collection_items           |   25976832
discussions                |   41041920
related_channels           |   54484992
channel_stat               |   58990592
channel                    |  377970688
video_scrape               |  403660800
caption                    |  614375424
pipeline                   |  979542016
video_recommendations      | 1741258752
augment                    | 1997570048
comments                   | 3990929408
video                      | 6693543936
video_stat                 | 6780289024
