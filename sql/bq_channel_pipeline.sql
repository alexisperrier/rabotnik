SELECT ch.channel_id, ch.title, ch.description, ch.country, ch.custom_url, ch.thumbnail, ch.origin, ch.activity_score, ch.activity,
ch.created_at, ch.retrieved_at,
p.status, p.lang, p.lang_conf,
cs.subscribers, cs.views, cs.videos
FROM channel ch
JOIN pipeline p ON p.channel_id = ch.channel_id
JOIN channel_stat cs ON cs.channel_id = ch.channel_id
WHERE p.status != 'incomplete'
