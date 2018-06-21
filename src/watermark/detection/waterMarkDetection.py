#!/usr/bin/python
# -*- coding:utf8 -*-

import os
import fileUtiles
import detectByMatching as dbm
import videoProcess
import rectProcess

#for output
import collections
import time

import json
import argparse

import numpy as np

parser = argparse.ArgumentParser(description='watermark detection parameter parser')
parser.add_argument('-i', type=str, dest='videoPath' ,help='input video full path')
parser.add_argument('-t', type=str, dest='intermediatePath', required=True, help='intermediate result save path')
parser.add_argument('-o', type=str, dest="res_output_path", help='result output path', default=None)
parser.add_argument('-p', type=str, dest="templatesfolder", help='template folder path')
parser.add_argument('-s', type=str, dest="templatesSuffix", default=".p", help='template file suffix')
parser.add_argument('-n', type=int, dest="sampledPicsNum", default=3, help='sampled pics count at each sample pos')
parser.add_argument('-c', '--clear', help="clear intermediate folder", action='store_true', default=False)
parser.add_argument('-v', '--verbose', help="enable debug", action='store_true', default=False)

def resultDataTransform(logoResults):
    newLogoResults = {}
    if not logoResults:
        return logoResults

    for logo in logoResults:
        rectArray = logoResults[logo]
        newLogoResults[logo] = []
        for rect in rectArray:
            newRect = {}
            newRect["x"] = rect[0][0]
            newRect["y"] = rect[0][1]
            w, h = rectProcess.calRectWidthAndHeight(rect)
            newRect["w"] = w
            newRect["h"] = h
            newLogoResults[logo].append(newRect)

    if len(newLogoResults) == 0:
        return None

    return newLogoResults



def printResult(code, msg, data, elapsedTime=None, doPrint=True):
    result = collections.OrderedDict()

    result["result_code"] = code

    if msg:
        result["result_msg"] = msg

    if data:
        newData = resultDataTransform(data)
        if newData:
            result["result_data"] = json.dumps(newData)

    if elapsedTime:
        result["elapsed_time"] = elapsedTime

    r = json.dumps(result)

    if doPrint:
        print r

    if result.has_key("result_data"):
        return result["result_data"]
    return None


def grabImages(videoFileName, grabedImageNum, imageIntermediatePath, dur, size=None):
    sampled_count = grabedImageNum
    maxDur = dur - 1
    if dur < 2:
        maxDur = dur

    sampledPos = np.arange(0, dur-1, float(dur)/grabedImageNum, dtype=float)

    id = 0
    for pos in sampledPos:
        seek_pos = videoProcess.second2hms(pos)
        videoProcess.grapImages(videoFileName, seek_pos, 3, imageIntermediatePath, "/{}%d.bmp".format(id), size)
        id = id + 1


def detectWatermarkInVideo(videoFileName, imageIntermediatePath, templateFolderPath, tempalte_suffix=".p", clearIntermediateFiles=False, grabedImageNum=5, openDebug=True):
    """
    detect different type logos in single video

    :param videoFileName:                    input video full path
    :param imageIntermediatePath:            folder for saving sampled pictures which will be used for detection
    :param templateFolderPath:               templates folder root path, may contains multiple sub-folders, each sub-folder contain one logo template
    :param tempalte_suffix                   template suffix
    :param clearIntermediateFiles            clear intermediate files after detection
    :param grabedImageNum                    number of sampled pictures in each sample pos of input video
    :param openDebug                         enable output debug results
    :return: result_description, result_dict
        result_description - fail or success
        result_dict        - dict of results, key - logo_type; value - array of log rect.
        e.g.: foramt like: "{\"douyin\": [[[406, 870], [523, 913]]], \"kuaishou\": [[[8, 7], [121, 47]]]}"
    """
    if not videoFileName or not imageIntermediatePath:
        return -1, "input params error", None

    videoFileName = videoFileName.strip()
    imageIntermediatePath = imageIntermediatePath.strip();

    video_metadata = videoProcess.findVideoMetada(videoFileName)
    if not video_metadata:
        return -2, "find video metadata fail", None

    stream_res_des, video_stream = videoProcess.getVideoStream(video_metadata)
    if not video_stream:
        return -3, stream_res_des, None

    dur_res_des, dur = videoProcess.getVideoDuration(video_stream)
    if not dur:
        return -4, dur_res_des, None

    size_res_des, size = videoProcess.getVideoSize(video_stream)
    if not size:
        return -5, size_res_des, None

    scaleParam = None

    grabImages(videoFileName, grabedImageNum, imageIntermediatePath, dur, scaleParam)

    return detectWatermarkInVideoByLocalPics(imageIntermediatePath, templateFolderPath, tempalte_suffix, ".bmp", clearIntermediateFiles, openDebug)


def detectWatermarkInVideoByLocalPics(imageIntermediatePath, templateFolderPath, tempalte_suffix=".p", pic_suffix=".bmp", clearIntermediateFiles=False, openDebug=True):
    if not templateFolderPath or not tempalte_suffix:
        return -6, "detect by pics: input params error", None

    imageIntermediatePath = imageIntermediatePath.strip()
    templateFolderPath = templateFolderPath.strip()
    tempalte_suffix = tempalte_suffix.strip()

    pfullPath, pflist = fileUtiles.eachFile(imageIntermediatePath, pic_suffix)
    if len(pfullPath) < 1:
        return -7, "sampled images less than 1", None

    k = dbm.detectWaterMarkSingleVideo(imageIntermediatePath, pfullPath, pflist, templateFolderPath, tempalte_suffix, openDebug)

    #clear intermediate data
    if not os.path.exists(imageIntermediatePath):
        os.mkdir(imageIntermediatePath)
    elif clearIntermediateFiles:
        pfullPath, pflist = fileUtiles.eachFile(imageIntermediatePath, pic_suffix)
        for pf in pfullPath:
            os.remove(pf)

    ret = None
    if k[0] == 0:
        ret = 0, k[1], None
    else:
        ret = 1, "success", k[2]

    return ret

if __name__ == '__main__':

    start = time.clock()
    args = parser.parse_args()

    res = None
    if args.videoPath:
        res = detectWatermarkInVideo(args.videoPath, args.intermediatePath, args.templatesfolder, args.templatesSuffix, args.clear, args.sampledPicsNum, args.verbose)
    else:
        res = detectWatermarkInVideoByLocalPics(args.intermediatePath, args.templatesfolder, args.templatesSuffix, ".jpg", args.clear, args.verbose)

    elapsedTime = (time.clock() - start)

    if res :
        if args.res_output_path:
            video_full_path = args.videoPath
            inter_path = args.intermediatePath
            file_name = None
            if video_full_path:
                file_name, suffix = fileUtiles.getFileNameAndSuffixFromPath(video_full_path.strip())
            elif inter_path:
                file_name = fileUtiles.getFolderNameFormPath(inter_path.strip())

        if res[0] == 1:
            rects = printResult(1, res[1], res[2], elapsedTime, True)

            if args.res_output_path:
                  if file_name and rects:
                    path = args.res_output_path.strip() + "/" + file_name + ".txt"
                    f = open(path, "wb")
                    f.write(rects)
                    f.close()
        else:
            printResult(res[0], res[1], None, elapsedTime, True)




