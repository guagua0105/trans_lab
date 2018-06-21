# !/usr/bin/python
# -*- coding: utf-8 -*-
elk_url = 'http://sla.weibo.cn/elasticsearch/_msearch'
appkey = '445670032'
url_ssig = '1'
ssig_api_str = 'http://i.api.weibo.com/statuses/get_ssig_url.json?source=%s&url=%s'
source_api_str = 'http://i2.api.weibo.com/2/object/show.json?source=%s&url_ssig=%s&object_id=%s'