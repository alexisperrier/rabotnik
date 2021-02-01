# Rabotnik

Rabotnik is a python based application to monitor the French youtube.

It centralizes multiple background jobs, each one with a specific task.
The end result is an _exhaustive_ database of all the videos published on youtube in France since .

The database is composed of
### channels
Over N millions French channels and N millions Foreign channels

- title and descriptions
- stats: subscribers, views, ...
-

### videos
Over N millions videos with

- title and descriptions
- views
- duration, thumbnails, ...
- publication date, ...

For some specific set of videos we also collect
- comments
- captions

### Recommendations

The video recommendations are obtained from a video page via scraping. This is a cold start scraping, without any profile personnalisation involved.
The recommendations are obtained soon (few days max) after the video is published.
Scraping of video recommendations is a complex task which is not activated full time and reserved for specific sets of videos.

# French vs Foreign

Most channels have a country field properly set.

We filter French vs Foreign videos and channels via
- the channels country field. Only half the

When the country value is missing, we look at the language of the video title and description to decide if the channel and related videos belongs to the French perimeter or if it is Foreign.

This is not 100% full proof but is simple enough.

# Data Sources

We use a mix of
- Channel RSS feed
- Youtube API V3
- and Video page Scrapping when needed. (complex and unstable)

Although most if not all the data is available via the Youtube API, using Rss feeds and scraping helps us stay within API quota limits.

Each Channel has an rss feed. For instance France24 rss feed is available at

Each feed shows the 15 most recent videos.

We use a channel feed:

- to filter out foreign channels
- to identify new published videos
- to get data on the channel upon discovery (mostly title and description)
- to get data on the new videos (title, description and publication date)
- estimate the publication rate of the channel (time span for the videos in the RSS feed )

Once a channel has been identified as French, its feed is parsed regularly.
If the channel is identified as foreign, we keep the feed information but do not parse its feed.



# Channel and video discovery
New channels are discovered via

- video recommendations. Each recommended video belongs to a channel. the *channel_triage* job assesses yet unknown channels.
- channel recommendations. Channels have the ability to recommend other channels. Think blogroll. The *complete_channels* job captures these recommendations
- upload of channel lists. The front end app (kansatsu) has a feature to upload lists of channels in specific collections. Each channel in the collection that is not yet in the database is sent to the *channel_triage* job for assessment.

New videos are discovered via:

- Video recommendations via the *video_scrape* job
- New videos discovered in the RSS feed via the *feed_parsing* job
- Video lists upload in specific collections via the Kansatsu app.

This discovery process is quite efficient and we discover most active channels and recently published videos.

# Jobs
Rabotnik works on multiple server instances in parallel via cron jobs.

- Instances specifics are set in config/config_rabotnik.json
- the *py* folder holds the main job scripts (called  _flows_)
- The *py/scripts* folder holds one time scripts for specific import exports and clean up operations
- ./sandbox.py and sql/sandbox.sql are _sandbox_ script hoolders used to test new scripts and debug.
- the *main.py* drives the execution and parametrization of the different flows

## Run a job

For instance, executing the *feed_parsing* job is done via

    python main.py -- --flowname feed_parsing

And the *complete_videos* job is executed via

    python main.py -- --flowname complete_videos

While the *video_scrape* job is run for 250 videos via

    python main.py -- --flowname video_scrape --max_items 250

The different job executions are set up in cron. See for instance the [template](https://github.com/alexisperrier/rabotnik/blob/master/sh/cron_template.sh) in ./sh/cron_template.sh

## Queuing

When a flow is executed via cron, the script estimates the number of items (channels, videos, comments, ...) that need processing and selects the 50 most pressing ones (criteria may vary according to the flow at hand)

Each API call is limited to 50 elements.

RSS feed and video page scraping are not limited to 50 items.

To allow for concurrent execution of the same script on multiple servers and avoid running the same script over the same batch of videos or channels, we set a *offset_factor* parameter in the config/congif_rabotnik.json file to act as buffer.

- offset_factor = 0: the first 50 items are processed
- offset_factor = 1: items 51 to 100 are processed
- offset_factor = 2: items 101 to 150 are processed

and so forth



## Code structure

A Flow (task) is composed of multiple operations

- flow.py defines by default operations. Holds parent Flow Class
- each flow_<xxxx>.py defines the specific operations for a given flow and defines the Flow<Xxxx> cLass
- model.py standard CRUD operations on tables
- db.py, api.db: wrapper around db and API
- job.py: drives the execution of the Flow
- text.py: NLP utils

# Db

Postgres database is hosted on Google Cloud Platform.

Simplest way to connect is by setting up a cloud_sql_proxy.

# BigQuery

[TODO] The data is regularly exported to Big Query for long term storage



# Install

## Youtube API key

Do not use multiple API keys to access the API but instead ask for higher quota limits if you are regularly running over.

We chose to host the keys in the database and not as environment variables.
This makes it easier to handle keys across multiple servers. But it may not be the most secure method.


## Database

The best way to create the database from scratch is to use the rake task of the kansatsu companion rails app. The database schema holds the up to date database structure.

The database is postgresql

For full text search we use ts_queries and store data natively as json.

## Cron jobs
See the [template](https://github.com/alexisperrier/rabotnik/blob/master/sh/cron_template.sh) in ./sh/cron_template.sh
