# -*- coding: UTF-8 -*-
import json
import src.parser.mediaParamParser as MediaParamParser
import src.parser.inputParser as InputParser
import src.define.mediaParams as MediaParams
import src.define.basedefine as basedefine
import src.media.batchTransQulity as BatchTransQulity
import src.define.input as inputStruct
import src.media.transcode as transcode
import src.score.quality_worker as qualityWorker
import tool.logger as logger

module_name = "worker.batch_quality_compare"

crf_trans_parm = "-dn -metadata:s rotate= -vcodec libx264 -crf %d -preset veryslow -movflags faststart -x264opts psy=0:ref=5:keyint=90:min-keyint=9:chroma_qp_offset=0:aq_mode=2:threads=36:lookahead-threads=4 -maxrate 2500k -bufsize 5M"
multipas1_trans_parm = "-dn -metadata:s rotate= -vcodec libx264 -b:v %dk -pass 1 -preset veryslow -movflags faststart -x264opts psy=0:ref=5:keyint=90:min-keyint=60:chroma_qp_offset=0:aq_mode=2:threads=36:lookahead-threads=4 -f mp4"
multipas2_trans_parm = "-dn -metadata:s rotate= -vcodec libx264 -b:v %dk -pass 2 -preset veryslow -movflags faststart -x264opts psy=0:ref=5:keyint=90:min-keyint=60:chroma_qp_offset=0:aq_mode=2:threads=36:lookahead-threads=4 -f mp4"

#  -maxrate %dk -bufsize 20M
def store(data, save_path):
    with open(save_path, "w") as f:
        json.dump(data, fp=f, indent=4)

def main_parser():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i", "--inputconfig", dest="inputconfig_path", help=r"input config path")
    parser.add_option("-o", "--outputconfig", dest="outputconfig_path", default=None, help=r"output config path")
    parser.add_option("-e", "--encodeconfig", dest="encodeconfig_path", default=None, help=r"encode param config")

    return parser

def doExperiment(opt):

    # params parser
    mediaParamParser = MediaParamParser.MediaParamParser()
    (res, baseMediaParams, baseVideoBitrateArray) = mediaParamParser.Parser(opt.encodeconfig_path)
    if res < 0:
        return

    inputParser =InputParser.InputParser()
    (res, baseInputArray) = inputParser.Parser(opt.inputconfig_path)
    if res < 0:
        return

    # params prepare
    show_size =basedefine.VideoSize()
    show_size.width = 1280
    show_size.height = 720

    logger.g_logger.info("start deel. ")


    batchTransQulity = BatchTransQulity.BatchTransQulity()
    batchTransQulity.setParams()




def _create_module_log():
    return logger.log2stdout(module_name)

if __name__ == "__main__":
    logger.g_logger = _create_module_log()

    parser = main_parser()
    (opt, args) = parser.parse_args()

    doExperiment(opt)
    logger.g_logger.info("end ==================")