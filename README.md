# Rabotnik

Back end for Kansatsu

Rabotnik retrieves all French video and channels from Youtube using
- Youtube API V3
- Channel RSS feeds
- Video page Scrapping

Rabotnik works on multiple server instances in parallel via cron jobs.

- Instances specifics are set in config/config_rabotnik.json
- scripts/ holds one time scripts for specific import exports and clean up operations

## Code structure

A Flow (task) is composed of multiple operations

- flow.py defines by default operations. Holds parent Flow Class
- each flow_<xxxx>.py defines the specific operations for a given flow and defines the Flow<Xxxx> cLass
- model.py standard CRUD operations on tables
- db.py, api.db: wrapper around db and API
- job.py: drives the execution of the Flow
- text.py: NLP utils

# Db

Postgres database is hosted on Google Cloud Platform

# Flows

## API
- channel and video information: titles, descriptions, publication dates ...
- channel and video stats: views, subscribers, ...
- video comments: 100 most popular
- video search by keywords

## Chanel Feed Parsing
- new video detection
- foreign / French status (triage)

## Scraping
- video: recommended videos and captions

## Other
- channel topic modeling
- care, helm: field conversions, monitoring
- index search: video data for the search engine as ts vectors


# Install
[WIP]
- define Youtube V3 api keys in the database
- create database (see rails schema in kansatsu)
- create cron jobs

TODO: Dockerize
