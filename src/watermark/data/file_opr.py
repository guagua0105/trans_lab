# -*- coding: UTF-8 -*-
import json
import os

def loadJson3(filename):
    file = open(filename, 'rb')
    buf = file.read()
    buf.replace(' ', '')  # 去掉空格
    buf.replace('\n', '')  # 去掉换行符
    buf.replace('\r\n|\r', '')  # 去掉换行符

    # buf.decode('utf-8-sig')
    print buf
    dic = json.loads(buf)
    return dic

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

def get_delogo_info_from_logfile(path):
    log = loadJson3(path)
    hits = None
    source = None
    if log.has_key("hits"):
        if log["hits"].has_key("hits"):
            hits = log["hits"]["hits"]
            if hits[0].has_key("_source"):
                source = hits[0]["_source"]
                if source.has_key("delogo_result_code") and source.has_key("delogo_result_msg") and source.has_key("delogo_result_data"):
                    return (source["delogo_result_code"], source["delogo_result_msg"],source["delogo_result_data"])
