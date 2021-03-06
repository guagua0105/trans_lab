# -*- coding: UTF-8 -*-
import src.watermark.data.file_opr
import os, sys
import shutil
import config.run_config as run_config
import subprocess
import shlex
import json
import requests
import datetime
import tool.logger as logger
import src.watermark.detection.videoProcess as videoProcess
import numpy as np
import src.network.video_downloader as video_downloader

module_name = "src.watermark.data.trans_pic_grab."

def _create_module_log():
    return logger.log2stdout(module_name)

# -*- inputmode -*-
# 0: 日志路径模式
# 1： 视频TOP Object_ID模式，输入格式为CVS
# -*- inputpath -*-
# string，取值为输入信息目录
# -*- outputpath -*-
# string，取值为输出目录
def main_parser():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-m", "--inputmode", dest="inputmode", type=int, default=None, help=r"input log path")
    parser.add_option("-i", "--inputlogpath", dest="inputpath", default=None, help=r"input path")
    parser.add_option("-o", "--outputpath", dest="outputpath", default=None, help=r"out log path")
    return parser

def get_oid(log):
    hits = None
    source = None
    if log.has_key("hits"):
        if log["hits"].has_key("hits"):
            hits = log["hits"]["hits"]
            if hits[0].has_key("_source"):
                source = hits[0]["_source"]
                if source.has_key("object_id"):
                    return source["object_id"]
    return None

def get_input_url(log):
    hits = None
    source = None
    if log.has_key("hits"):
        if log["hits"].has_key("hits"):
            hits = log["hits"]["hits"]
            if hits[0].has_key("_source"):
                source = hits[0]["_source"]
                if source.has_key("input_url"):
                    return source["input_url"]

def get_input_url_from_logfile(path):
    log = src.watermark.data.file_opr.loadJson3(path)
    hits = None
    source = None
    if log.has_key("hits"):
        if log["hits"].has_key("hits"):
            hits = log["hits"]["hits"]
            if hits[0].has_key("_source"):
                source = hits[0]["_source"]
                if source.has_key("input_url"):
                    return source["input_url"]

def get_delogo_info(log):
    hits = None
    source = None
    if log.has_key("hits"):
        if log["hits"].has_key("hits"):
            hits = log["hits"]["hits"]
            if hits[0].has_key("_source"):
                source = hits[0]["_source"]
                if source.has_key("delogo_result_code") and source.has_key("delogo_result_msg") and source.has_key("delogo_result_data"):
                    return (source["delogo_result_code"], source["delogo_result_msg"],source["delogo_result_data"])

def get_delogo_info_from_logfile(path):
    log = src.watermark.data.file_opr.loadJson3(path)
    hits = None
    source = None
    if log.has_key("hits"):
        if log["hits"].has_key("hits"):
            hits = log["hits"]["hits"]
            if hits[0].has_key("_source"):
                source = hits[0]["_source"]
                if source.has_key("delogo_result_code") and source.has_key("delogo_result_msg") and source.has_key("delogo_result_data"):
                    return (source["delogo_result_code"], source["delogo_result_msg"],source["delogo_result_data"])


def get_unique_log(log_output_path, unique_log_output_path, max_log_num=None, sub_folder=False):

    if not os.path.exists(unique_log_output_path):
        os.mkdir(unique_log_output_path)

    fps, fns = src.watermark.data.file_opr.eachFile(log_output_path, '.json')

    unique_source_video_dic = {}
    id =0
    for f in fps:
        id = id + 1
        if max_log_num and id > max_log_num:
            break

        log = src.watermark.data.file_opr.loadJson3(f)
        oid = get_oid(log)
        print oid
        if oid:
            if not unique_source_video_dic.has_key(oid):
                unique_source_video_dic[oid] = f
                new_path = None
                if sub_folder:
                    new_folder_path = unique_log_output_path + "/" + oid + "/"
                    if not os.path.exists(new_folder_path):
                        os.mkdir(new_folder_path)
                    new_path = new_folder_path + oid + ".json"
                else:
                    new_path = unique_log_output_path + oid + ".json"

                shutil.copy(f, new_path)
                print new_path
                print  get_delogo_info(log)

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
        buf = subprocess.check_output(cmdargs,stderr=subprocess.STDOUT)  ####确认是否为block型的操作
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

def grab1Pic(input_url, output_fullpath, seek_pos='00:00:03', count=1):

    print ("seek_pos =")
    if not seek_pos:
        return 1

    cmd = ["%s -y -threads 0" % run_config.ffmpeg]
    cmd.append('-i \"%s\"' % input_url)
    cmd.append('-ss %s' % seek_pos)
    cmd.append('-vframes {:d}'.format(count))
    cmd.append('%s' % output_fullpath)
    processcmd = ' '.join(cmd)
    print ("ffmpeg cmd =")
    process = subprocess.Popen(processcmd, shell=True)
    process.wait()

    return 0

def updataUrl(url):
    url = "http://i.api.weibo.com/statuses/get_ssig_url.json?source=445670032&url=" + url

    r = requests.get(url)

    if r.status_code < 300:
        jobj = json.loads(r.content)
        if jobj.has_key("result_data"):
            if jobj["result_data"].has_key("ssig_url"):
                return jobj["result_data"]["ssig_url"]

    return ""

def downloadFile(url, local_path):
    r = requests.get(url)
    with open(local_path, "wb") as code:
        code.write(r.content)

def grabVideoPic(input_log_json_path, output_path, sample_num=1, sub_folder=False, file_mode=None):
    log = src.watermark.data.file_opr.loadJson3(input_log_json_path)
    oid = get_oid(log)
    input_url = get_input_url(log)
    print input_url

    output_file_path_f = output_path
    output_file_path_b = output_path
    if sub_folder:
        output_file_path_f = output_path + oid + "/" + oid
        output_file_path_b = output_path + oid + "/" + oid
    else:
        output_file_path_f = output_path + oid
        output_file_path_b = output_path + oid

    if sample_num > 1 and file_mode:
        output_file_path_f = output_file_path_f + "_f" + file_mode
        output_file_path_b = output_file_path_b + "_b" + file_mode
    else:
        output_file_path_f = output_file_path_f + "_f.jpg"
        output_file_path_b = output_file_path_b + "_b.jpg"

    input_url = updataUrl(input_url)
    print input_url
    print output_file_path_f
    print output_file_path_b

    # get video duraion

    video_metadata = findVideoMetada(input_url)
    if not video_metadata:
        print "find video metadata fail"

    if not video_metadata.has_key("streams"):
        print "video meta parse error"

    video_stream = None
    for stream in video_metadata["streams"]:
        if stream.has_key("codec_type"):
            if stream["codec_type"] == "video":
                video_stream = stream
                break

    if not video_stream:
        print "no video stream"

    print video_stream
    dur = None
    if video_stream.has_key("duration"):
        dur = video_stream["duration"]
    else:
        print "duration parse error"

    if not dur:
        print "duration parse error"

    if dur == "":
        print "duration parse error"

    if float(dur) < 0:
        print "duration is negative"
    dur = float(dur)

    grab1Pic(input_url, output_file_path_f, "00:00:00", sample_num)
    print "grab front image done"
    if dur > 1.0:
        m, s = divmod(dur - 1, 60)
        h, m = divmod(m, 60)
        seek_pos = "%02d:%02d:%02d" % (h, m, s)
        grab1Pic(input_url, output_file_path_b, seek_pos, sample_num)
        print "grab back image done"
    else:
        print "dur less than 1s"

    print "-------------------------------------------"

def grabVideoPics1(bkts, output_path, sub_folder=False):

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    videoDownloader = video_downloader.VideoDownloader()
    for bkt in bkts:
        oid = bkt
        print "input_url: ", oid

        # 添加防盗链
        input_url = videoDownloader.get_ssig_url_with_original(oid)
        print "input_url: ", input_url

        #get video duraion
        video_metadata = findVideoMetada(input_url)
        if not video_metadata:
            print "find video metadata fail"
            continue

        if not video_metadata.has_key("streams"):
            print "video meta parse error"
            continue

        video_stream = None
        for stream in video_metadata["streams"]:
            if stream.has_key("codec_type"):
                if stream["codec_type"] == "video":
                    video_stream = stream
                    break

        if not video_stream:
            print "no video stream"
            continue

        print video_stream
        dur = None
        if video_stream.has_key("duration"):
            dur = video_stream["duration"]
        else:
            print "duration parse error"
            continue

        if not dur:
            print "duration parse error"
            continue

        if dur == "":
            print "duration parse error"
            continue

        if float(dur) < 0:
            print "duration is negative"
            continue
        dur = float(dur)

        # create file name
        output_file_path_f = output_path
        if sub_folder:
            output_file_path = output_path + "/" + oid + "/"
            if output_file_path:
                if not os.path.exists(output_file_path):
                    os.mkdir(output_file_path)

            output_file_path_f = output_path + "/" + oid + "/" + oid
        else:
            output_file_path_f = output_path + "/" + oid

        print "pic output path:",output_file_path_f

        # grab the pic
        grabImages(input_url,3,output_file_path_f,dur,3)
        print "-------------------------------------------"

def grabVideoPics2(log_path, output_path, max_log_num=None, sample_num=1, sub_folder=False, file_mode=None):

    if not os.path.exists(output_path):
        os.mkdir(output_path)


    fps, fns = src.watermark.data.file_opr.eachFile(log_path, ".json")

    file_num = 0
    front_pic = 0
    back_pic = 0

    start_flag = False
    for fp in fps:
        print fp

        file_num = file_num + 1
        if max_log_num and file_num > max_log_num:
            break

        json_fullpath = fp
        print "current log path:", json_fullpath

        log = src.watermark.data.file_opr.loadJson3(json_fullpath)
        oid = get_oid(log)
        input_url = get_input_url(log)
        print "input url:", input_url

        # 添加防盗链
        input_url = updataUrl(input_url)
        print "updated url: ", input_url

        #get video duraion
        video_metadata = findVideoMetada(input_url)
        if not video_metadata:
            print "find video metadata fail"
            continue

        if not video_metadata.has_key("streams"):
            print "video meta parse error"
            continue

        video_stream = None
        for stream in video_metadata["streams"]:
            if stream.has_key("codec_type"):
                if stream["codec_type"] == "video":
                    video_stream = stream
                    break

        if not video_stream:
            print "no video stream"
            continue

        print video_stream
        dur = None
        if video_stream.has_key("duration"):
            dur = video_stream["duration"]
        else:
            print "duration parse error"
            continue

        if not dur:
            print "duration parse error"
            continue

        if dur == "":
            print "duration parse error"
            continue

        if float(dur) < 0:
            print "duration is negative"
            continue
        dur = float(dur)

        # create file name
        output_file_path_f = output_path
        if sub_folder:
            output_file_path = output_path + oid + "/"
            if output_file_path:
                if not os.path.exists(output_file_path):
                    os.mkdir(output_file_path)

            output_file_path_f = output_path + oid + "/" + oid
        else:
            output_file_path_f = output_path + oid

        print "pic output path:",output_file_path_f

        # grab the pic
        grabImages(input_url,3,output_file_path_f,dur,3)
        print "-------------------------------------------"

def grabImages(videoFileName, grabedImageNum, imageIntermediatePath, dur, sample_num, size=None):
    sampled_count = grabedImageNum
    maxDur = dur - 1
    if dur < 2:
        maxDur = dur

    sampledPos = np.arange(0, dur-1, float(dur)/grabedImageNum, dtype=float)

    id = 0
    for pos in sampledPos:
        seek_pos = videoProcess.second2hms(pos)
        videoProcess.grapImages(videoFileName, seek_pos, sample_num, imageIntermediatePath, "_{}_%d.jpg".format(id), size)
        id = id + 1


def get_unique_log_and_grab_pics(log_output_path, unique_log_output_path, max_log_num=None):
    unique_logs = unique_log_output_path
    # get_unique_log(log_output_path, unique_log_output_path, 1000, True)
    get_unique_log(log_output_path, unique_log_output_path, max_log_num)

    #print get_delogo_info_from_logfile("/Users/liuwen/Development/test/trans_lab/unique_output/4230282997709506.json")

    # grabVideoPics(unique_logs, unique_logs, 1000, 10, True, "%d.jpg")
    # grabVideoPics(unique_logs, unique_logs, max_log_num)

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')     # <! 中文设置
    logger.g_logger = _create_module_log()

    #get opt
    parser = main_parser()
    (opt, args) = parser.parse_args()
    logger.g_logger.info("********* start ********")

    if opt.inputmode == 0:
        # 根据日志开始截图
        grabVideoPics2(opt.inputpath, opt.outputpath, 4995, 3, True, "%d.jpg")
    elif opt.inputmode == 1:
        bkts = ["1034:4257655233946385", "1034:4257704869331637"]
        grabVideoPics1(bkts, opt.outputpath, True)

    logger.g_logger.info("********* end ********")




