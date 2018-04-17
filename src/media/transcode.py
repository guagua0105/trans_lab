# -*- coding: UTF-8 -*-
import tool.sys_execute as sys_execute
import time
import config.run_config as run_config
import json
import tool.logger as logger

# input_path 输入文件路径
# input_params 输入文件处理参数
# stream_select 处理媒体流选择
# vrate_params 视频码率相关设置
# vencoder_params 视频编码参数设置
# vfilter_params 视频图像处理设置，如水印、缩放等
# format_params 格式设置
# aencoder_params 音频编码设置
# output_path 输出文件设置
class TransParams:
    def __init__(self):
        self.input_params = ''
        self.input_path = ''
        self.stream_select = ''
        self.vrate_params = ''
        self.vencoder_params = ''
        self.vfilter_params = ''
        self.aencoder_params = ''
        self.format_params = ''
        self.output_path = ''

# transParams：transcode params
def transcode(transParams):
    cmd_string = '%s -hide_banner -y -threads 0 %s %s %s %s %s %s %s %s %s'
    transcode_cmd = cmd_string % (run_config.ffmpeg, transParams.input_params, transParams.input_path, transParams.stream_select,
                                  transParams.vfilter_params, transParams.vrate_params, transParams.vencoder_params,
                                  transParams.aencoder_params, transParams.format_params, transParams.output_path)
    logger.g_logger.info("start trans: %s" % transcode_cmd)

    start_time = time.time()
    (returnCode, output) = sys_execute.execute(transcode_cmd)
    if returnCode:
        logger.g_logger.error("failed trans")
        return (1,0)
    end_time = time.time()

    return (0,(end_time - start_time))

def transcode(path,trans_parm,outputpath):
    cmd_string = '%s -hide_banner -y -threads 0 %s %s %s'
    transcode_cmd = cmd_string % (run_config.ffmpeg, path,trans_parm,outputpath)
    logger.g_logger.info("start trans: %s" % transcode_cmd)

    start_time = time.time()
    (returnCode, output) = sys_execute.execute(transcode_cmd)
    if returnCode:
        logger.g_logger.error("failed trans")
        return (1,0)
    end_time = time.time()

    return (0,(end_time - start_time))


def getStreamInfo(video):

    cmd_string = '%s -v 16 -select_streams v -show_streams -print_format json %s'
    probe_cmd = cmd_string % (run_config.ffprobe, video)
    logger.g_logger.debug("subprocess = %s" % probe_cmd)
    (returnCode, output) = sys_execute.execute(probe_cmd)
    if returnCode:
        logger.g_logger.error("failed probe")
        return None
    info = json.loads(output)
    vinfo = info[u'streams'][0]
    return vinfo











