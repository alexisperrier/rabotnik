MAILTO=""

# Manually set the timing of each job according to the server and the exected volume of content
# Executing the .bash_profile (MAC) or .bash_rc allows to load environment settings ($PATH, variables, ...)

*/30 * * * * . $HOME/.bash_profile; <path to python>/python <path to rabotnik>/main.py -- --flowname video_scrape --max_items 250 >> <path to rabotnik>/log/scrape.log

*/7 * * * * . $HOME/.bash_profile; <path to python>/python <path to rabotnik>/main.py -- --flowname feed_parsing >> <path to rabotnik>/log/feed_parsing.log

*/4 * * * * . $HOME/.bash_profile; <path to python>/python <path to rabotnik>/main.py -- --flowname channel_triage >> <path to rabotnik>/log/channel_triage.log

1-59/2 * * * * . $HOME/.bash_profile; <path to python>/python <path to rabotnik>/main.py -- --flowname video_stats >> <path to rabotnik>/log/video_stats.log

1-59/2 * * * * . $HOME/.bash_profile; <path to python>/python <path to rabotnik>/main.py -- --flowname channel_stats >> <path to rabotnik>/log/channel_stats.log

1-59/2 * * * * . $HOME/.bash_profile; <path to python>/python <path to rabotnik>/main.py -- --flowname index_search >> <path to rabotnik>/log/index_search.log

1-59/2 * * * * . $HOME/.bash_profile; <path to python>/python <path to rabotnik>/main.py -- --flowname complete_videos >> <path to rabotnik>/log/complete_videos.log

*/10 * * * * . $HOME/.bash_profile; <path to python>/python <path to rabotnik>/main.py -- --flowname video_comments >> <path to rabotnik>/log/video_comments.log

1-59/5 * * * * . $HOME/.bash_profile; <path to python>/python <path to rabotnik>/main.py -- --flowname complete_channels >> <path to rabotnik>/log/complete_channels.log

*/2 * * * * . $HOME/.bash_profile; <path to python>/python <path to rabotnik>/oneshot.py >> <path to rabotnik>/log/oneshot.log
