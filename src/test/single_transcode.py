# -*- coding: UTF-8 -*-
import os,sys
import time
import subprocess
import logger
import json
import ctypes

module_name = "worker.quality_lab_from_json"


ffmpeg = "/Users/yangle/Work/github/trans_codec/key_test/ffmpeg"
ffprobe = "/Users/yangle/Work/github/trans_codec/key_test/ffprobe"

class BaseOutput:
    def __init__(self):
        self.transcode_time = -1
        self.crf = -1
        self.result = -1


class BaseOutputArray:
    def __init__(self):
        self._n = 0
        self._capacity = 100
        self._A = self._make_array(self._capacity)  # low-level array

    def __len__(self):
        return self._n

    def __getitem__(self, k):
        if not 0 <= k < self._n:
            raise IndexError('invalid index')
        return self._A[k]

    def append(self, BaseInput):
        if self._n == self._capacity:
            self._resize(2 * self._capacity)

        self._A[self._n] = BaseInput
        self._n += 1

    def _resize(self, c):
        B = self._make_array(c)
        for k in range(self._n):
            B[k] = self._A[k]
            self._A = B
            self._capacity = c

    def _make_array(self, c):
        return (c * ctypes.py_object)()

    def convert2json(self):
        json = {}
        for i in range(0, self._n):
            # one file deel
            output = self.__getitem__(i)
            json[i] = output.__dict__

        return json

def execute(command):
    try:
        logger.g_logger.debug("subprocess = " + str(command))
        process = subprocess.Popen(command, stdout=None, stderr=None, shell=True)
        output, error = process.communicate()
        if process.returncode:
            logger.g_logger.error("error[{:d}]: \n{:s}".format(process.returncode, error))
            return (process.returncode, None)
        #logger.g_logger.debug("\n" + output + error)
        return (0, output)
    except Exception as e:
        logger.g_logger.error("Exception = `%s`" % str(e));
        raise e

    return (1, None)

def getStreamInfo(video):

    cmd_string = '%s -v 16 -select_streams v -show_streams -print_format json %s'
    probe_cmd = cmd_string % (ffprobe, video)
    logger.g_logger.debug("subprocess = %s" % probe_cmd)
    (returnCode, output) = execute(probe_cmd)
    if returnCode:
        logger.g_logger.error("failed probe")
        return None
    info = json.loads(output)
    vinfo = info[u'streams'][0]
    return vinfo

def transcode(path,trans_parm,outputpath):
    cmd_string = '%s -hide_banner -y -threads 0 -i %s %s %s'
    transcode_cmd = cmd_string % (ffmpeg, path,trans_parm,outputpath)
    logger.g_logger.info("start trans: %s" % transcode_cmd)

    start_time = time.time()
    (returnCode, output) = execute(transcode_cmd)
    if returnCode:
        logger.g_logger.error("failed trans")
        return (1,0)
    end_time = time.time()

    return (0,(end_time - start_time))

def _create_module_log():
    return logger.log2stdout(module_name)

trans_parm_base = "-dn -an -metadata:s rotate= -vcodec libx264 -crf %d -preset slow"

def main_parser():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i", "--inputpath", dest="input_path", default=None, help=r"N video to be download")
    parser.add_option("-o", "--outputpath", dest="output_path", default=None, help=r"json saved path")
    parser.add_option("-w", "--workdir", dest="work_dir", default=None, help=r"video save dir")
    return parser

def do_experiment(path, outputpath):
    logger.g_logger = _create_module_log()
    logger.g_logger.info("********* start ********")

    trans_crf = 26
    baseOutputArray = BaseOutputArray()
    while trans_crf > 24:
        output = BaseOutput()
        output.crf = trans_crf
        trans_parm = trans_parm_base % trans_crf
        (output.result,output.transcode_time) = transcode(path, trans_parm, outputpath)

        baseOutputArray.append(output)
        trans_crf = trans_crf - 1

    outputDict = baseOutputArray.convert2json()
    logger.g_logger.info("weibo [lab_info]: %s", outputDict)
    logger.g_logger.info("********* end ********")


if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')     # <! 中文设置

    parser = main_parser()
    (opt, args) = parser.parse_args()
    do_experiment(opt.input_path, opt.output_path)

