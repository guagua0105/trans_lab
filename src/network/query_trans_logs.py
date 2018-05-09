# -*- coding: UTF-8 -*-
import subprocess
import json
import os
import config.elk_query_config_single_log_query as elk_config
import file_opr


def do_elk_aggregation(top_num=None, result_prefix=None, elk_index=None, elk_query=None, elk_field=None):

    top_param = "-n {:d}".format(top_num)
    result_prefix_param = "-j {:s}".format(result_prefix)

    cmd = [ "python", \
            "test_top_video_downloader.py"
            ]

    if top_num:
        cmd.append("-n {:d}".format(top_num))
    if result_prefix:
        cmd.append("-j {:s}".format(result_prefix))
    if elk_index:
        cmd.append("-i {:s}".format(elk_index))
    if elk_field:
        cmd.append("-d {:s}".format(elk_field))
    if elk_query:
        cmd.append("-q {:s}".format(elk_query))

    print ''.join(cmd)

    retval = subprocess.call(cmd, 0, None, None, None, None)
    print 'return =', retval
    return retval

def do_elk_single_log_query(index=None, program=None, query_key=None, query_value=None, output_path=None, result_prefix=None):

    cmd = [ "python", \
            "query_single_log.py"
            ]

    if result_prefix:
        cmd.append("-j {:s}".format(result_prefix))
    if index:
        cmd.append("-i {:s}".format(index))
    if program:
        cmd.append("-g {:s}".format(program))
    if query_key:
        cmd.append("-k {:s}".format(query_key))
    if query_value:
        cmd.append("-v {:s}".format(query_value))
    if output_path:
        cmd.append("-o {:s}".format(output_path))

    print ''.join(cmd)

    retval = subprocess.call(cmd, 0, None, None, None, None)
    print 'return =', retval
    return retval

if __name__ == "__main__":
    #1. download samples
    top_num = 10000
    result_prefix = "sample_top"
    do_elk_aggregation(top_num, result_prefix)

    # 2. download log
    sample_list_result_path = None
    pwd = os.getcwd()
    fps, fns = file_opr.eachFile(pwd)
    for f in fps:
        if f.find(result_prefix):
            sample_list_result_path = f
            break

    print "sample list name:",sample_list_result_path

    sample_list_result = file_opr.loadJson3(sample_list_result_path)

    print sample_list_result

    if sample_list_result.has_key('responses'):
        if sample_list_result['responses'][0].has_key('aggregations'):
            buckets = sample_list_result['responses'][0]['aggregations']['topN']['buckets']
            idx = 0
            for bucket in buckets:
                url = bucket["key"]
                print url

                prefix = "log-" + str(idx) + "-"
                log_output_path = "/Users/liuwen/Development/test/trans_lab/output/"
                do_elk_single_log_query("logstash-mweibo-", "weibo_video_trans", "output_url", url, log_output_path, prefix)
                idx = idx + 1
                # break
        else:
            print "aggregations not exist"

        pass





