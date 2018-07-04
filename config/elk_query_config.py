# !/usr/bin/python
# -*- coding: utf-8 -*-

# "query": "programname:mweibo_client_video AND video_mediaid:1034*"
# "field": "video_mediaid"

#elk_query = "programname:mweibo_client_video AND video_mediaid:1034*"
#elk_query_field = "video_mediaid"

# elk_query = "programname:mweibo_client_video AND video_source:story"
# elk_query_field = "video_url"

elk_query_index = "logstash-mweibo-"
elk_query = "programname:weibo_video_trans AND job_type:TRANS_STORY AND prev_height:1280 AND prev_width:720 AND file_duration:>10"
elk_query_field = "input_url"

