# -*- coding: UTF-8 -*-
import transcode
import time
import config.run_config as run_config
import json
import tool.logger as logger
import src.define.mediaParams as mediaParams
import src.define.input as inputStruct
import src.define.output as outputStruct
import src.score.quality_worker as qualityWorker


class TransQulity:
    def setParams(self, baseVideoBitrate, baseMediaParams, baseInput, showSize):
        self.baseVideoBitrate = baseVideoBitrate
        self.baseMediaParams = baseMediaParams
        self.baseInput = baseInput
        self.showSize = showSize


    def transAndQulity(self):
        baseOutput = outputStruct.BaseOutput()
        transParams = transcode.TransParams()
        transParams.input_path = self.baseInput.input_path
        output_path = transParams.input_path
        output_path.replace('.mp4','-tmp.mp4')
        transParams.stream_select = '-dn -an'
        transParams.vfilter_params = self.baseMediaParams.vfilter_params
        transParams.vencoder_params = self.baseMediaParams.vencoder_params
        transParams.aencoder_params = self.baseMediaParams.aencoder_params
        transParams.format_params = self.baseMediaParams.format_params

        if self.baseVideoBitrate == mediaParams.RC_2_PASS:

            vrate_params_pass1 = "-b:v %dk -pass 1"
            transParams.vrate_params = vrate_params_pass1 % (self.baseVideoBitrate.output_bitrate)
            transParams.output_path = "/dev/null"

            (returnCode, transcode_time) = transcode.transcode(transParams)
            if returnCode:
                logger.g_logger.info("failed to transcode")
                return (-1, None)
            baseOutput.transcode_time += transcode_time

            vrate_params_pass2 = "-b:v %dk -pass 2"
            transParams.vrate_params = vrate_params_pass2 % (self.baseVideoBitrate.output_bitrate)
            transParams.output_path = output_path
            (returnCode, transcode_time) = transcode.transcode(transParams)

            if returnCode:
                logger.g_logger.info("failed to transcode")
                return (-1, None)
            baseOutput.transcode_time += transcode_time
            logger.g_logger.info("multipass end trans transcode_time %d *************************************" % baseOutput.transcode_time)

        else:

            vrate_params_crf = "-crf %d"
            transParams.vrate_params = vrate_params_crf % (self.baseVideoBitrate.crf)
            transParams.output_path = output_path

            (returnCode, transcode_time) = transcode.transcode(transParams)
            if returnCode:
                logger.g_logger.info("failed to transcode")
                return (-1, None)
            baseOutput.transcode_time += transcode_time
            logger.g_logger.info("crf end trans transcode_time %d *************************************" % baseOutput.transcode_time)

        # --------------------------------------------
        # get stream info
        srcInfo = transcode.getStreamInfo(input.input_path)
        dstInfo = transcode.getStreamInfo(transParams.output_path)
        if not srcInfo:
            return (-1, None)
        if not dstInfo:
            return (-1, None)

        baseOutput.output_path = output_path
        baseOutput.output_bitrate = int(dstInfo.get(u'bit_rate', 0)) / 1000

        # ---------------------------------------------
        # vmaf value
        qualityDealer = qualityWorker.VMAFQualityWorker()
        baseOutput.score = qualityDealer.get_score(input.input_path, transParams.output_path, srcInfo, dstInfo, input.vmaf_result_path, self.showSize)

        return (1,baseOutput)