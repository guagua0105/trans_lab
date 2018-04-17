# -*- coding: UTF-8 -*-
import json
import src.define.input as inputStruct
import src.define.output as outputStruct
import src.media.transcode as transcode
import src.score.quality_worker as qualityWorker
import tool.logger as logger
import src.define.basedefine as basedefine

module_name = "worker.base_quality_compare"

#  -maxrate %dk -bufsize 20M
def store(data, save_path):
    with open(save_path, "w") as f:
        json.dump(data, fp=f, indent=4)

def main_parser():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-s", "--srcpath", dest="src_path", help=r"src path")
    parser.add_option("-d", "--dstpath", dest="dst_path", default=None, help=r"dst path")
    parser.add_option("-r", "--resultinfo", dest="result_path", default=None, help=r"result info")

    return parser

def doExperiment(src_path, dst_path, result_path):
    # --------------------------------------------
    # get stream info
    srcInfo = transcode.getStreamInfo(src_path)
    dstInfo = transcode.getStreamInfo(dst_path)
    if not srcInfo:
        return (-1,0)
    if not dstInfo:
        return (-1,0)

    dst_bitrate = int(dstInfo.get(u'bit_rate', 0)) / 1000

    show_size = basedefine.VideoSize()
    show_size.width = 720
    show_size.height = 1280
    # ---------------------------------------------
    # vmaf value
    qualityDealer = qualityWorker.VMAFQualityWorker()
    compare_score = qualityDealer.get_score(src_path, dst_path, srcInfo, dstInfo, result_path,show_size)


    logger.g_logger.info("score show info: *************************************")

    logger.g_logger.info("compare_score=%f, dst_bitrate=%f" % (float(compare_score), float(dst_bitrate)))
    return (compare_score, dst_bitrate)

def _create_module_log():
    return logger.log2stdout(module_name)

if __name__ == "__main__":
    logger.g_logger = _create_module_log()

    parser = main_parser()
    (opt, args) = parser.parse_args()
    #if main_check(opt):
    #    exit(1)
    (compare_score, dst_bitrate) = doExperiment(opt.src_path, opt.dst_path, opt.result_path)
    logger.g_logger.info("end ==================")