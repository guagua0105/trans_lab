# -*- coding: UTF-8 -*-
import os, sys
import json
import tool.logger as logger
import time
import elk_searcher_query_single_log

module_name = "worker.test_top_video_downloader"

def main_parser():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-j", "--json", dest="json", default="log", help=r"json saved path")
    parser.add_option("--hours", dest="hours", type=int, default=24, help=r"search in how many hours")
    parser.add_option("-f", "--overwrite", dest="overwrite", action="store_true", default=True, help=r"force overwrite existing file")
    parser.add_option("-p", "--point", dest="timepoint", default="now", help=r"now, yesterday, or time in '%Y.%m.%d-%H' format")
    parser.add_option("--start-epoch", dest="start_epoch", type=float, default=0, help=r"start eposh.")
    parser.add_option("--end-epoch", dest="end_eposh", type=float, default=0, help=r"end eposh.")
    parser.add_option("-o", "--outputdir", dest="outputdir", default=None, help=r"output json save dir")
    parser.add_option("-i", "--elk_query_index", dest="elk_query_index", default="", help=r"index type")
    parser.add_option("-g", "--programname", dest="programname", default="", help=r"programname name")
    parser.add_option("-k", "--query_key", dest="query_key", default="", help=r"query key")
    parser.add_option("-v", "--query_value", dest="query_value", default="", help=r"query value")

    return parser

def main_check(opt):
    if not opt.start_epoch:
        opt.end_epoch = time.time()
        if opt.timepoint =="yesterday":
            st = time.gmtime(opt.end_epoch)
            st = time.strptime(time.strftime("%Y.%m.%d", st), "%Y.%m.%d")   #零晨
            opt.end_epoch = time.mktime(st) - 1
            opt.hours = 24
        elif opt.timepoint != "now":
            st = time.strptime(opt.timepoint, "%Y.%m.%d-%H")
            opt.end_epoch = time.mktime(st) - 1
    if not opt.start_epoch:
        opt.start_epoch = opt.end_epoch - opt.hours * 3600 + 1
    setattr(opt, "start_time", time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(opt.start_epoch)))
    setattr(opt, "end_time", time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(opt.end_epoch)))

    logger.g_logger.info("search FROM {:s} TO {:s}".format(opt.start_time, opt.end_time))
    if opt.end_epoch - opt.start_epoch < 60*30:
        logger.g_logger.error("search duration less than 30-min maybe useless\n")
        return 1
    opt.json = "{:s}[{:s} - {:s}].json".format(opt.json, time.strftime('%Y.%m.%d-%H', time.localtime(opt.start_epoch)) ,time.strftime('%Y.%m.%d-%H', time.localtime(opt.end_epoch)))
    print opt.json
    return 0

def _create_module_log():
    return logger.log2stdout(module_name)

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')     # <! 中文设置
    logger.g_logger = _create_module_log()

    #
    parser = main_parser()
    (opt, args) = parser.parse_args()
    logger.g_logger.info("********* start ********")
    logger.g_logger.info("opt=\n"+str(opt))
    if main_check(opt):
        exit(1)
    elkSearcherMediaid = elk_searcher_query_single_log.ElkSearcherQuerySingleLog()
    buckets = elkSearcherMediaid.get_search_result(opt)



