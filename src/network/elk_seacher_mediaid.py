# -*- coding: UTF-8 -*-
import elk_searcher
import json
import time
import tool.logger as logger
import config.elk_query_config as elk_config

class ElkSearcherMediaid(elk_searcher.ElkSearcher):

    def generate_query_json(self, opts):
        start_date = time.strftime('%Y.%m.%d', time.localtime(opts.start_epoch))
        end_date = time.strftime('%Y.%m.%d', time.localtime(opts.end_epoch))

        query_index = {
            "index": ['logstash-video-' + start_date],
            "ignore_unavailable": True,
            # "preference": 1494948626374
        }
        if end_date != start_date:
            query_index["index"].append('logstash-video-' + end_date)

        query_data = {
            "size": 0,
            "query": {
                "bool": {
                    "must": [{
                        "query_string": {
                            "analyze_wildcard": True,
                            "query": elk_config.elk_query
                        }
                    }, {
                        "range": {
                            "@timestamp": {
                                "gte": 1000 * int(opts.start_epoch),
                                "lte": 1000 * int(opts.end_epoch),
                                "format": "epoch_millis"
                            }
                        }
                    }
                    ],
                    "must_not": []
                }
            },
            "_source": {
                "excludes": []
            },
            "aggs": {
                "topN": {
                    "terms": {
                        "field": elk_config.elk_query_field,
                        "size": int(opts.topN),
                        "order": {
                            "_count": "desc"
                        }
                    }
                }
            }
        }

        setattr(opts, "query_index", query_index)
        setattr(opts, "query_data", query_data)

        query_json_str = "{:s}\n{:s}\n".format(query_index, query_data)
        query_json = json.dumps(query_json_str)
        query_json = query_json.replace('\\n', '\n')
        query_json = query_json[1:-1]
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
            ret_dict["query_index"] = opts.query_index
            ret_dict["query_data"] = opts.query_data
            #with open(opts.json, "wb") as f:
                #json.dump(ret_dict, f, indent=4)
            logger.g_logger.info("save resopnse data in " + opts.json)
        responses = ret_dict['responses']
        buckets = responses[0]['aggregations']['topN']['buckets']
        top_count = 0
        for element in buckets:
            # print element['key'], element['doc_count']
            top_count += element['doc_count']
        all_count = responses[0]["hits"]["total"]
        logger.g_logger.info("return top-{N:d} {top_count:d}/{all_count:d}={pecent:.2f}%".format(
            N=len(buckets), top_count=top_count, all_count=all_count,
            pecent=top_count * 100 / all_count))
        return buckets