# !/usr/bin/python
# -*- coding: utf-8 -*-

# "query": "programname:mweibo_client_video AND video_mediaid:1034*"
# "field": "video_mediaid"

elk_query = "programname:mweibo_client_video AND video_mediaid:1034*"
elk_query_field = "video_mediaid"

elk_story_query = "programname:mweibo_client_video AND video_source:story AND (video_width:540 OR video_height:544)"
elk_story_query_field = "video_url"