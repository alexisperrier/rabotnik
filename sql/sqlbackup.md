# Backup sql and Migration

Goal is
- Create database backup on OVH instance
- Migrate from Google SQL to OVH instance

## Prerequisite

- gcloud installed
    - see https://cloud.google.com/sdk/docs/install

- postgresql-11 installed

- about 50 Gb of free space
    - check with df -h

## 1 Export data to local
### 1.1 Connect to db

- set proxy for connection from Google SQL to local

    see https://cloud.google.com/sql/docs/mysql/quickstart-proxy-test#linux-64-bit
    ./cloud_sql_proxy -instances=<INSTANCE_CONNECTION_NAME>=tcp:3306
    with
    INSTANCE_CONNECTION_NAME as ytagora:us-east4:ytkojo-prod
    ./cloud_sql_proxy -instances=ytagora:us-east4:ytkojo-prod=tcp:3306
    add & at the end to run as background process

- set database password
- connect via:
    psql -h 127.0.0.1 -p 3307 -U postgres ytkojo-proddb -W

## 1.2 export db to local backup

- list all tables
select table_name, pg_relation_size(quote_ident(table_name))
from information_schema.tables
where table_schema = 'public'
order by 2

     yt_categories              |             8192
     users                      |             8192
     collections                |             8192
     schema_migrations          |             8192
     query                      |            24576
     searches                   |            24576
     helm                       |           229376
     flow                       |          1122304
     topic                      |         23437312
     collection_items           |         25976832
     discussions                |         41041920
     related_channels           |         54484992
     channel_stat               |         58990592
     channel                    |        377905152
     video_scrape               |        403390464
     caption                    |        614170624
     pipeline                   |        979542016
     video_recommendations      |       1740488704
     augment                    |       1996857344
     comments                   |       3990872064
     video                      |       6687744000
     video_stat                 |       6777503744


- run pg_dump for all tables

pg_dump -h 127.0.0.1 -p 3307 -U postgres --format plain --verbose --file yt_categories.sql --table public.yt_categories ytkojo-proddb -W



## 2. Create database on local

### 2.1 connection

Troubleshooting
https://gist.github.com/AtulKsol/4470d377b448e56468baef85af7fd614


- create local postgresql database

<!-- psql -U username -d database -1 -f your_dump.sql -->
psql -U postgres -d ytkojodb -1 -f yt_categories.sql

### 2.2 custom types
see all custom types with \dT
These types must be created manually before importing the dumps
- CREATE TYPE apikey_status AS ENUM ('active','standby','invalid');
- CREATE TYPE caption_status AS ENUM ('acquired','unavailable','queued','error');


- create tables and indexes
- load data from sql backuped files

## 3. Open remote access to database

- password protected

- migrate backend rabotnik
- migrate frontend ragnar
