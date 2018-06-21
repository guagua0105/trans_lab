# -*- coding: UTF-8 -*-
import urllib2
import tool.logger as logger
import os, sys
import config.url_config_single_log_query as url_config
from abc import abstractmethod

class ElkSearcher2():

    @abstractmethod
    def generate_query_json(self, opts):
        raise NotImplementedError

    @abstractmethod
    def get_search_result(self, opts):
        raise NotImplementedError

    # 生成查询的http header
    def post_topvideo_query(self, opts):
        query_url = url_config.elk_url
        query_json = self.generate_query_json(opts)
        logger.g_logger.info("query_url=\n" + query_url)
        logger.g_logger.info("query_data=\n" + query_json)
        print "query_json:",query_json

        query_post = urllib2.Request(query_url, query_json)
        query_post.add_header('Content-Type', 'application/json')

        logger.g_logger.info('post_topvideo_query open...')
        try:
            query_post_inst = urllib2.urlopen(query_post)
        except urllib2.URLError as e:
            logger.g_logger.error('Query post failed! URLError : {:s}'.format(str(e.reason)))
            return None
        except urllib2.HTTPError as e:
            logger.g_logger.error('Query post failed! HTTPError code ({:d}), ({:s})'.format(e.code, e.read()))
            return None

        logger.g_logger.info('post_topvideo_query reading...')
        try:
            response = query_post_inst.read()
        except Exception, e:
            logger.g_logger.error('Query post read() failed!')
            return None

        logger.g_logger.info('post_topvideo_query End...')
        logger.g_logger.debug('response=\n' + response)
        return response

    def checkoutput(self, output, b_overwrite):
        if os.path.isfile(output):
            if not b_overwrite:
                logger.g_logger.warning(output + " already exist")
                return 1
            else:
                logger.g_logger.warning(output + " would be overwrite")
        return 0