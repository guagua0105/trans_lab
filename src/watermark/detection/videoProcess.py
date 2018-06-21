#!/usr/bin/python
# -*- coding:utf8 -*-

# for ffmpeg probe
import os
import subprocess
import shlex
import json
import config.run_config as run_config
import datetime
import signal
import time

def grapImages(filename, startTime, count, outputpath, fileModel, size=None):
    if startTime:
      ss = "-ss " + startTime
    else:
      ss = ""

    str0 = run_config.ffmpeg+" -y -threads 0 "
    inputf = " -i " + filename
    str1 = " -vframes " + str(count) + " "

    if size:
        str1 = str1 + size + " "

    outputf = outputpath + fileModel
    if ss == "":
        str0 = str0 + inputf + str1 + " " + outputf
    else:
        str0 = str0 + ss + inputf + str1 + " " + outputf

    p = subprocess.Popen(shlex.split(str0), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    timeout = 5
    start = datetime.datetime.now()
    while p.poll() is None:
        time.sleep(0.02)
        now = datetime.datetime.now()
        if (now - start).seconds > timeout:
            try:
                os.kill(p.pid, signal.SIGKILL)
                os.waitpid(-1, os.WNOHANG)
            except:
                pass
            return False
    return True

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

    p = subprocess.Popen(cmdargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    timeout = 5
    start = datetime.datetime.now()
    while p.poll() is None:
        time.sleep(0.02)
        now = datetime.datetime.now()
        if (now - start).seconds > timeout:
            try:
                os.kill(p.pid, signal.SIGKILL)
                os.waitpid(-1, os.WNOHANG)
            except:
                pass
            return None

    output, unused_err = p.communicate()
    return output

def execProgram2(cmdargs):
    try:
        buf = subprocess.check_output(cmdargs)  ####确认是否为block型的操作
    except subprocess.CalledProcessError as e:
        return None

    output = None
    if not buf == '':
        output = json_loads_byteified(buf)

    return output

def findVideoMetada(pathToInputVideo):
    cmd = run_config.ffprobe + " -v quiet -print_format json -show_streams"
    args = shlex.split(cmd)
    args.append(pathToInputVideo)
    return execProgram(args)

def getVideoDurationV1(filename):
    str1 = "2>&1 | grep \"Duration\"| cut -d \' \' -f 4 | sed s/,// | sed 's@\..*@@g' | awk \'{ split($1, A, \":\"); split(A[3], B, \".\"); print 3600*A[1] + 60*A[2] + B[1]}\'"
    str0 = "ffmpeg -i "
    str0 = str0 + filename + " " + str1
    fd = os.popen(str0)
    val = fd.read()
    fd.close()

    return val



def timeString2Second(t):
    h,m,s = t.strip().split(":")
    return int(h) * 3600 + int(m) * 60 + int(float(s))

def getVideoStream(video_metadata):
    video_stream = None
    if not video_metadata.has_key("streams"):
        return "video meta no streams tag", None

    for stream in video_metadata["streams"]:
        if stream.has_key("codec_type"):
            if stream["codec_type"] == "video":
                video_stream = stream
                break

    if  video_stream:
        return "success", video_stream
    else:
        return  "stream no codec_type tag", None


def getVideoDuration(video_stream):
    if video_stream.has_key("duration"):
        dur = video_stream["duration"]
    elif video_stream.has_key("tags"):
        if video_stream["tags"].has_key("DURATION"):
            dur = video_stream["tags"]["DURATION"]
            if dur:
                dur = timeString2Second(dur)
                return "success", dur
        else:
            return "duration parse error", None

    if not dur:
        return "duration parse error", None

    if dur == "":
        return "duration parse error", None

    if float(dur) < 0:
        return "duration is negative", None

    dur = int(float(dur) + 0.5) #检查是否包含小数点后一位

    return "success", dur

def getVideoSize(video_stream):
    height = None
    width = None

    if video_stream.has_key("height"):
        height = video_stream["height"]
    else:
        return "video size parse fail", None

    if video_stream.has_key("width"):
        width = video_stream["width"]
    else:
        return "video size parse fail", None

    if height == "" or width == "":
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
        return "invalide video size", None

    return "success", (height, width)

def second2hms(second):
    m, s = divmod(int(second), 60)
    h, m = divmod(m, 60)
    hms = "%02d:%02d:%02d" % (h, m, s)
    return hms
