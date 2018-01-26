# -*- coding: UTF-8 -*-
import json
import src.define.input as inputStruct
import src.define.output as outputStruct
import src.media.transcode as transcode
import src.score.quality_worker as qualityWorker
import tool.logger as logger

module_name = "worker.quality_lab_from_json"

trans_parm1 = '-pix_fmt yuv420p -vcodec libx264 -x264opts psy=0:ref=5:keyint=300:min-keyint=250:scenecut=0:b-pyramid=normal:mixed-refs=1:chroma_qp_offset=3:aq_mode=2:8x8dct=1:threads=36:lookahead-threads=4 -copyts -preset veryslow -crf 27 -f mp4 -preset veryfast'
trans_parm2 = '-pix_fmt yuv420p -vcodec libx264 -x264opts psy=0:ref=5:keyint=300:min-keyint=300:scenecut=0:chroma_qp_offset=3:aq_mode=2:threads=36:lookahead-threads=4:aq-strength=1.20:deblock=1,-3,-3 -copyts -preset veryslow -crf 25'
trans_parm3 = '-pix_fmt yuv420p -vcodec libx264 -x264opts psy=0:ref=5:keyint=300:min-keyint=300:scenecut=0:chroma_qp_offset=3:aq_mode=2:threads=36:lookahead-threads=4:aq-strength=1.20:deblock=1,-3,-3 -copyts -preset veryfast -crf 25'


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
    for i in range(0, len(inputs)):
        input = inputStruct.BaseInput()
        input.input_path = inputs[str(i)]["input_path"]
        input.input_trans_path = inputs[str(i)]["trans_file_path"]
        input.vmaf_result_path = inputs[str(i)]["vmaf_result_path"]
        BaseInputArray.append(input)

    # exec Experiment
    BaseOutputArray = outputStruct.BaseOutputArray()
    for i in range(0, len(BaseInputArray)):
        input = BaseInputArray.__getitem__(i)
        output = outputStruct.BaseOutput()
        logger.g_logger.info("start deel count %d *************************************" % i)

        # --------------------------------------------
        # transcode
        (returnCode, output.transcode_time) = transcode.transcode(input.input_path, input.input_trans_path, trans_parm3)

        if returnCode:
            logger.g_logger.info("failed to transcode")
            return

        # --------------------------------------------
        # get stream info
        srcInfo = transcode.getStreamInfo(input.input_path)
        dstInfo = transcode.getStreamInfo(input.input_trans_path)

        logger.g_logger.info("end trans transcode_time %d *************************************" % output.transcode_time)

        if not srcInfo:
            return
        if not dstInfo:
            return

        output.output_bitrate = dstInfo.get(u'bit_rate', 0)

        # ---------------------------------------------
        # vmaf value
        qualityDealer = qualityWorker.VMAFQualityWorker()
        output.score = qualityDealer.get_score(input.input_path, input.input_trans_path, srcInfo, dstInfo, input.vmaf_result_path)
        logger.g_logger.info("end deel count %d *************************************" % i)


        BaseOutputArray.append(output)

    logger.g_logger.info("all trans done. save to %s *************************************" % outputconfig_path)
    outputDict = BaseOutputArray.convert2json()
    store(outputDict, outputconfig_path)


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