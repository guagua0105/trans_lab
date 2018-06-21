# !/usr/bin/python
# -*- coding: utf-8 -*-

# "query": "programname:mweibo_client_video AND video_mediaid:1034*"
# "field": "video_mediaid"

elk_query = "programname:mweibo_client_video AND video_mediaid:1034*"
elk_query_field = "video_mediaid"

# elk_query = "programname:mweibo_client_video AND video_source:story"
# elk_query_field = "video_url"

elk_query_index = "logstash-mweibo-"
elk_query = "programname:weibo_video_trans AND (job_type:TRANS_STORY OR job_type:TRANS_VIDEO_SLOW) AND error_code:600 AND _exists_:delogo_result_code"
elk_query_field = "output_url"

