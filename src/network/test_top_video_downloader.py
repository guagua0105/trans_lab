# -*- coding: UTF-8 -*-
import os, sys
import json
import tool.logger as logger
import time
import elk_seacher_mediaid
import video_downloader

module_name = "worker.test_top_video_downloader"

def main_parser():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-n", "--top", dest="topN", type=int, default=50, help=r"N video to be download")
    parser.add_option("-j", "--json", dest="json", default="top", help=r"json saved path")
    parser.add_option("-V", "--vdir", dest="vdir", default=None, help=r"video save dir")
    parser.add_option("-f", "--overwrite", dest="overwrite", action="store_true", default=False, help=r"force overwrite existing file")
    parser.add_option("--hours", dest="hours", type=int, default=24, help=r"search in how many hours")
    parser.add_option("-p", "--point", dest="timepoint", default="now", help=r"now, yesterday, or time in '%Y.%m.%d-%H' format")
    parser.add_option("--start-epoch", dest="start_epoch", type=float, default=0, help=r"start eposh.")
    parser.add_option("--end-epoch", dest="end_eposh", type=float, default=0, help=r"end eposh.")
    parser.add_option("--tpl", dest="tpl_regex", default='[1,2,5,6]', help=r"template regex")
    parser.add_option("--downl", dest="b_downl", action="store_true", default=False, help="whether download videos")
    return parser

def main_check(opt):
    if opt.topN <= 0:
        logger.g_logger.error("topN <= 0 is not allowed")
        return 1
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
    setattr(opt, "start_time", time.strftime('%Y.%m.%d-%H:%M:%S', time.localtime(opt.start_epoch)))
    setattr(opt, "end_time", time.strftime('%Y.%m.%d-%H:%M:%S', time.localtime(opt.end_epoch)))
    logger.g_logger.info("search FROM {:s} TO {:s}".format(opt.start_time, opt.end_time))
    if opt.end_epoch - opt.start_epoch < 60*30:
        logger.g_logger.error("search duration less than 30-min maybe useless\n")
        return 1
    opt.json = "{:s}-{:d}.[{:s}].json".format(opt.json, opt.topN, time.strftime('%Y.%m.%d-%H', time.localtime(opt.end_epoch)))
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
    elkSearcherMediaid = elk_seacher_mediaid.ElkSearcherMediaid()
    videoDownloader = video_downloader.VideoDownloader()
    buckets = elkSearcherMediaid.get_search_result(opt)
    if opt.b_downl:
        for bkt in buckets:
            videoDownloader.videoDownload(bkt["key"], odir=opt.vdir, b_overwrite=opt.overwrite)


