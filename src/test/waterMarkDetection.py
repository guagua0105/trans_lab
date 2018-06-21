# coding=utf-8
import os

import detectByMatching as dbm

#for output
import collections
import time

# for ffmpeg probe
import subprocess
import shlex
import json
import argparse
import logging

parser = argparse.ArgumentParser(description='watermark detection parameter parser')
parser.add_argument('-i', type=str, dest='videoPath', required=True ,help='input video full path')
parser.add_argument('-t', type=str, dest='intermediatePath', required=True, help='intermediate result save path')
parser.add_argument('-th', type=float, dest="minSuccessDetectRate", required=True, help='min image detect success rate')
parser.add_argument('-v', action='store_true', dest='verbose', default=None, help='Enable debug info')

logger = logging.getLogger('[watermark]')
logger.setLevel(logging.DEBUG)
hdr = logging.StreamHandler()
formatter = logging.Formatter('%(name)s:%(levelname)s: %(message)s')
hdr.setFormatter(formatter)
logger.addHandler(hdr)
logger.setLevel(logging.ERROR)

def grapImages(filename, startTime, count, outputpath, fileModel):
    if startTime:
      ss = "-ss " + startTime
    else:
      ss = ""

    str0 = "ffmpeg -y -threads 0 "
    inputf = " -i " + filename
    str1 = " -vframes " + str(count) + " "
    outputf = outputpath + fileModel
    if ss == "":
        str0 = str0 + inputf + str1 + " " + outputf
    else:
        str0 = str0 + ss + inputf + str1 + " " + outputf

    FNULL = open(os.devnull, 'w')#这个需不需要关闭？
    logger.debug("cmd: %s", str0)
    p = subprocess.Popen(shlex.split(str0), stdout=FNULL, stderr=subprocess.STDOUT)
    p.communicate()

def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )

def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data

def execProgram(cmdargs):
    if not cmdargs:
        return None

    try:
        buf = subprocess.check_output(cmdargs)  ####确认是否为block型的操作
    except subprocess.CalledProcessError as e:
        logger.debug("%s", "command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        return None

    output = None
    if not buf == '':
        output = json_loads_byteified(buf)

    return output

def findVideoMetada(pathToInputVideo):
    cmd = "ffprobe -v quiet -print_format json -show_streams"
    args = shlex.split(cmd)
    args.append(pathToInputVideo)
    return execProgram(args)

def getVideoDuration(filename):
    str1 = "2>&1 | grep \"Duration\"| cut -d \' \' -f 4 | sed s/,// | sed 's@\..*@@g' | awk \'{ split($1, A, \":\"); split(A[3], B, \".\"); print 3600*A[1] + 60*A[2] + B[1]}\'"
    str0 = "ffmpeg -i "
    str0 = str0 + filename + " " + str1
    fd = os.popen(str0)
    val = fd.read()
    fd.close()
    logger.debug( "output: %s", val)

    return val

def eachFile(filePath, selectedExt=None):
    fileFullPathList = []
    fileNameList = []
    pathDir = os.listdir(filePath)
    for allDir in pathDir:
        if allDir == ".DS_Store":
            continue
        child = os.path.join('%s/%s' % (filePath, allDir))
        selected = False
        if not selectedExt == None:
            root, ext = os.path.splitext(child)
            if ext == selectedExt:
                selected = True
        else:
            selected = True

        if selected:
            fileFullPathList.append(child)
            fileNameList.append(allDir)

    return fileFullPathList, fileNameList

def printResult(code, msg, data):
    result = collections.OrderedDict()
    result["result_code"] = code
    result["result_msg"] = msg
    data_str = ''
    if data:
        for logo in data:
            if logo:
                for rect in logo:
                    if not data_str == '':
                        data_str = data_str + ", "
                    data_str = data_str + '({}, {}, {}, {})'.format(rect[0][0], rect[0][1], rect[1][0], rect[1][1])
        result["result_data"] = data_str
    r = json.dumps(result)
    print r
    pass


def timeString2Second(t):
    h,m,s = t.strip().split(":")
    return int(h) * 3600 + int(m) * 60 + int(float(s))

def getVideoDuration(video_stream):
    if video_stream.has_key("duration"):
        dur = video_stream["duration"]
    elif video_stream.has_key("tags"):
        if video_stream["tags"].has_key("DURATION"):
            dur = video_stream["tags"]["DURATION"]
            dur = timeString2Second(dur)
            return "success", dur
        else:
            printResult(-4, "duration parse error", None) ############
            return "duration parse error", None

    if not dur:
        printResult(-4, "duration parse error", None)
        return "duration parse error", None

    if dur == "":
        printResult(-4, "duration parse error", None)
        return "duration parse error", None

    if float(dur) < 0:
        printResult(-5, "duration is negative", None)
        return "duration is negative", None

    dur = int(float(dur) + 0.5) #检查是否包含小数点后一位

    return "success", dur

def detectWatermarkInVideo(videoFileName, imageIntermediatePath, minSuccessDetectRate=0.4, openDebug=False):
    """
    在单个视频内检测水印的位置

    :param videoFileName: 待检测视频的全路径
    :param imageIntermediatePath: 用户保存临时中间结果的路径
    :param minSuccessDetectRate: 最低检测成功阀值,default=0.4
    :return: 返回一个tumple:(结果字符串, (所有水印位置))，格式为：(string, tumple)
        结果字符串：包含三类
            错误：内容为错误原因
            检测失败：内容为"fail"
            检测成功：内容为"success"，例如：'success'表示成功检测到两个水印
        (所有水印位置) = ((rect),...,(rect)))
            (rect) = (矩形左上角点，矩形右下角点).
            特殊情况：失败、检测失败是返回None
        返回值例子：
            错误：("no video stream", None)
            失败：(fail, None)
            成功：('success', [[((8, 15), (121, 56)), ((2, 57), (220, 85))], [((409, 874), (522, 915)), ((309, 916), (527, 944))]])

    """

    video_metadata = findVideoMetada(videoFileName)
    if not video_metadata:
        printResult(-1, "find video metadata fail", None)
        return "find video metadata fail", None

    if not video_metadata.has_key("streams"):
        printResult(-2, "video meta parse error", None)
        return "video meta parse error", None

    video_stream = None
    for stream in video_metadata["streams"]:
        if stream.has_key("codec_type"):
            if stream["codec_type"] == "video":
                video_stream = stream
                break

    if not video_stream:
        printResult(-3, "no video stream", None)
        return "no video stream", None

    dur_res_des, dur = getVideoDuration(video_stream)

    if not dur:
        return dur_res_des, None

    height = None
    width = None

    if video_stream.has_key("height"):
        height = video_stream["height"]
    else:
        printResult(-6, "video size parse fail", None)
        return "video size parse fail", None

    if video_stream.has_key("width"):
        width = video_stream["width"]
    else:
        printResult(-6, "video size parse fail", None)
        return "video size parse fail", None

    if height == "" or width == "":
        printResult(-6, "video size parse fail", None)
        return "video size parse fail", None

    rotated = 0
    if video_stream.has_key("tags"):
        video_tags = video_stream["tags"]
        if video_tags.has_key("rotate"):
            rotate = int(video_tags["rotate"])
            if (abs(rotate) == 90) or (abs(rotate) == 270):
                rotated = 1

    if rotated == 0:
        height = int(height)
        width = int(width)
    else:
        tmpwidth = width
        tmpheight = height
        height = int(tmpwidth)
        width = int(tmpheight)

    if height <= 0 or width <= 0:
        printResult(-7, "invalide video size", None)
        return "invalide video size", None

    fm = "/f%d.bmp"
    grapImages(videoFileName, "", 10, imageIntermediatePath, fm)

    if dur > 1:
        fm = "/b%d.bmp"
        grapImages(videoFileName, "00:00:" + str(int(dur) - 1), 10, imageIntermediatePath, fm)


    pfullPath, pflist = eachFile(imageIntermediatePath, '.bmp')
    if len(pfullPath) < 10:
        printResult(-10, "sampled images less than 10", None)
        return "sampled images less than 10", None

    k = dbm.detectWaterMarkSingleVideo(imageIntermediatePath, pfullPath, pflist, minSuccessDetectRate, openDebug)

    logger.debug( "final res: %s",k)

    #clear intermediate data
    if not os.path.exists(imageIntermediatePath):
        os.mkdir(imageIntermediatePath)
    else:
        pfullPath, pflist = eachFile(imageIntermediatePath, '.bmp')
        for pf in pfullPath:
            os.remove(pf)

    if k[0] <= 0:
        printResult(0, "fail", k[1])
        return "fail", k[1]
    else:
        printResult(1, "success", k[1])
        ret = "success " + str(k[0])
        return ret, k[1]

if __name__ == '__main__':

    start = time.clock()
    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)

    detectWatermarkInVideo(args.videoPath, args.intermediatePath, args.minSuccessDetectRate)
    elapsed = (time.clock() - start)
    print elapsed


