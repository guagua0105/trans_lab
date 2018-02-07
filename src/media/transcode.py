# -*- coding: UTF-8 -*-
import tool.sys_execute as sys_execute
import time
import config.run_config as run_config
import json
import tool.logger as logger

# input_param：input media list; input param
# trans_param：trans param
# output_param：output media list; output param
def transcode(input_param,output_param,trans_param):
    cmd_string = '%s -hide_banner -y %s %s %s'
    transcode_cmd = cmd_string % (run_config.ffmpeg, input_param, trans_param, output_param)
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











