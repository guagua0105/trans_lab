# -*- coding: UTF-8 -*-
import json
import src.define.input as inputStruct
import src.define.output as outputStruct
import src.media.transcode as transcode
import src.score.quality_worker as qualityWorker
import tool.logger as logger
import src.define.basedefine as basedefine

module_name = "worker.compare_encoding"

crf_trans_parm = "-dn -metadata:s rotate= -vcodec libx264 -crf %d -preset veryslow -movflags faststart -x264opts psy=0:ref=5:keyint=90:min-keyint=9:chroma_qp_offset=0:aq_mode=2:threads=36:lookahead-threads=4 -maxrate 2500k -bufsize 5M"
crf_trans_parm2 = "-dn -metadata:s rotate= -vcodec libx264 -crf %d -preset veryslow -movflags faststart -x264opts psy=0:ref=5:keyint=90:min-keyint=9:chroma_qp_offset=0:aq_mode=2:threads=36:lookahead-threads=4 -maxrate 2200k -bufsize 10M"

#  -maxrate %dk -bufsize 20M
def store(data, save_path):
    with open(save_path, "w") as f:
        json.dump(data, fp=f, indent=4)

def main_parser():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i", "--inputconfig", dest="inputconfig_path", help=r"input config path")
    parser.add_option("-o", "--outputconfig", dest="outputconfig_path", default=None, help=r"output config path")

    return parser

def doExperiment(inputconfig_path, outputconfig_path):
    BaseInputArray = inputStruct.BaseInputArray()
    with open(inputconfig_path,'r') as json_file:
        inputInfo = json.load(json_file)

    logger.g_logger.info("start deel. ")
    inputs = inputInfo
    show_size =basedefine.VideoSize()
    show_size.width = 1280
    show_size.height = 720
    for i in range(0, len(inputs)):
        input = inputStruct.BaseInput()
        input.input_path = inputs[str(i)]["input_path"]
        input.input_trans_path = inputs[str(i)]["trans_file_path"]
        input.vmaf_result_path = inputs[str(i)]["vmaf_result_path"]
        BaseInputArray.append(input)

    # exec Experiment
    for i in range(0, len(BaseInputArray)):
        input = BaseInputArray.__getitem__(i)
        trans_crf = int(25)

        while trans_crf < 26:
            logger.g_logger.info("start deel count %d *************************************" % i)

            input_param = '-i ' + input.input_path

            # --------------------------------------------
            # crf transcode
            video_trans_parm = crf_trans_parm % trans_crf
            (returnCode, crf_transcode_time) = transcode.transcode(input_param, input.input_trans_path, video_trans_parm)

            if returnCode:
                logger.g_logger.info("failed to transcode")
                return

            # --------------------------------------------
            # get stream info
            srcInfo = transcode.getStreamInfo(input.input_path)
            dstInfo = transcode.getStreamInfo(input.input_trans_path)

            logger.g_logger.info("crf end trans transcode_time %d *************************************" % crf_transcode_time)

            if not srcInfo:
                return
            if not dstInfo:
                return

            crf_output_bitrate = int(dstInfo.get(u'bit_rate', 0)) / 1000

            # ---------------------------------------------
            # vmaf value
            qualityDealer = qualityWorker.VMAFQualityWorker()
            crf_trans_score = float(qualityDealer.get_score(input.input_path, input.input_trans_path, srcInfo, dstInfo, input.vmaf_result_path,show_size))


            # ---------------------------------------------
            # compare encoding

            video_trans_parm2 = crf_trans_parm2 % trans_crf
            (returnCode2, crf_transcode_time2) = transcode.transcode(input_param, input.input_trans_path, video_trans_parm2)

            if returnCode2:
                logger.g_logger.info("failed to transcode")
                return

            # --------------------------------------------
            # get stream info
            srcInfo = transcode.getStreamInfo(input.input_path)
            dstInfo = transcode.getStreamInfo(input.input_trans_path)

            logger.g_logger.info("compare crf end trans transcode_time %d *************************************" % crf_transcode_time)

            if not srcInfo:
                return
            if not dstInfo:
                return

            compare_crf_output_bitrate = int(dstInfo.get(u'bit_rate', 0)) / 1000

            # ---------------------------------------------
            # vmaf value
            qualityDealer = qualityWorker.VMAFQualityWorker()
            compare_crf_trans_score = qualityDealer.get_score(input.input_path, input.input_trans_path, srcInfo, dstInfo, input.vmaf_result_path,show_size)


            logger.g_logger.info("score show info: *************************************")

            logger.g_logger.info("crf:%f,crf_trans_score:%f,crf_output_bitrate=%f,compare_crf_trans_score:%f，compare_crf_trans_bitrate:%f" % (float(trans_crf),float(crf_trans_score),float(crf_output_bitrate), float(compare_crf_trans_score), float(compare_crf_output_bitrate)))
            trans_crf = int(trans_crf) +1





def _create_module_log():
    return logger.log2stdout(module_name)

if __name__ == "__main__":
    logger.g_logger = _create_module_log()

    parser = main_parser()
    (opt, args) = parser.parse_args()
    #if main_check(opt):
    #    exit(1)
    doExperiment(opt.inputconfig_path, opt.outputconfig_path)
    logger.g_logger.info("end ==================")