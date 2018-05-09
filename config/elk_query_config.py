# !/usr/bin/python
# -*- coding: utf-8 -*-

# "query": "programname:mweibo_client_video AND video_mediaid:1034*"
# "field": "video_mediaid"

# "query": "programname:mweibo_client_video AND video_source:story"
# "field": "video_url"

# elk_query = "programname:mweibo_client_video AND video_source:story"
# elk_query_field = "video_url"

elk_query_index = "logstash-mweibo-"
elk_query = "programname:weibo_video_trans AND _exists_: delogo_result_code AND error_code: 600"
elk_query_field = "output_url"