<!--
This is a dump of the database schema exported in rails
Storage 43.872 Gb
 -->

## Kansatsu only
* User: kansatsu, empty
* users: kansatsu

### Exports for collections
* active_storage_attachments: attachements for exports in kansatsu. Not used. empty
* active_storage_blobs: attachements for exports in kansatsu. Not used. empty
* export_items: exports  in kansatsu. Not used. empty
* exports: exports  in kansatsu. Not used. empty

## Core tables
* augment: base for search on videos.  4M rows, 3.1Gb
* channel: table for channels, 0.52 Gb
* pipeline: 1.7Gb
* video: 10Gb
* channel_stat: channels stats 0.1 Gb
* related_channels: list of friendly channels, blogroll. 110 Mb 500k
* video_recommendations: 5Gb,
* video_stat: stats for videos

* comments: 6Gb, 12.5 M
* discussions: 400k

* topic: channels topics
* yt_categories
* query: holds the sql Queries used to id the next items for processing

### Collections
* collection_items: collections videos and channels
* collections
* searches: record of searches, used to create collection based on search

### Monitoring
* flow: handles processing of videos and channels
* helm: clean up and volumes for each flow

# tables that can be dropped
exp_related_videos_01
origin
plot
related_videos_02
related_videos_export
timer
video_stat_01

# TODO
- augment: rm indexing for videos older than N months.
- pipeline: rm rows with video_id not null?
