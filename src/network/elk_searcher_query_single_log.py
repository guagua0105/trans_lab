# -*- coding: UTF-8 -*-
import elk_searcher2
import json
import os
import time
import tool.logger as logger
import config.elk_query_config_single_log_query as elk_config


class ElkSearcherQuerySingleLog(elk_searcher2.ElkSearcher2):

    def generate_query_json(self, opts):
        start_date = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(opts.start_epoch))
        end_date = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(opts.end_epoch))

        if not opts.elk_query_index == '':
            elk_config.elk_query_index = opts.elk_query_index.lstrip()

        if not opts.programname == '':
            elk_config.programname = opts.programname.lstrip()

        if not opts.query_key == '':
            elk_config.query_key = opts.query_key.lstrip()

        if not opts.query_value == '':
            elk_config.query_value = opts.query_value.lstrip()

        time_stamp = ''
        if end_date != start_date:
            time_stamp = end_date + "~" + end_date
        else:
            time_stamp = "now-1d"


        query_data = {
            "fields": {
                "programname": elk_config.programname,
                elk_config.query_key: elk_config.query_value
            },
            "indexName": elk_config.elk_query_index,
            "timeFormat": "day",
            "timestamp": "now-1d",
            "isDetail": "yes"
        }

        query_json = json.dumps(query_data)
        print "query_json:",query_json
        query_json = query_json.replace('\\n', '\n')
        query_json = query_json.replace("'", '"')
        query_json = query_json.replace('True', 'true')
        return query_json


    def get_search_result(self, opts):
        ret_json = self.post_topvideo_query(opts)
        if ret_json == None:
            logger.g_logger.error('Could not get top video!')
            return
        ret_dict = json.loads(ret_json)
        if not self.checkoutput(opts.json, opts.overwrite):
            # save query data aside response data
            ret_dict["query_time"] = "{:s} ~ {:}".format(opts.start_time, opts.end_time)
            ret_dict["query_index"] = opts.elk_query_index
            ret_dict["query_key"] = opts.query_key
            ret_dict["query_value"] = opts.query_value
            ret_dict["programname"] = opts.programname


            jsonPath = None
            if opts.outputdir:
                jsonPath = opts.outputdir
                idx = jsonPath.find('/')
                if idx > 0:
                    jsonPath = jsonPath[idx:]
                if not os.path.exists(jsonPath):
                    os.mkdir(jsonPath)

                if not jsonPath[-1] == "/":
                    jsonPath = jsonPath + "/"
                jsonPath = jsonPath + opts.json
            else:
                jsonPath = opts.json

            with open(jsonPath, "wb") as f:
                json.dump(ret_dict, f, indent=4)
            logger.g_logger.info("save resopnse data in " + jsonPath)
        hits = None
        source = None
        if ret_dict.has_key("hits"):
            if ret_dict["hits"].has_key("hits"):
                hits = ret_dict["hits"]["hits"]
                if hits[0].has_key("_source"):
                    source = hits[0]["_source"]
        else:
            return None

        # for s in source:
        #     print s
        return source