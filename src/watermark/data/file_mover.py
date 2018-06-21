# -*- coding: UTF-8 -*-
import os, sys, shutil
#import tool.logger as logger

module_name = "src.watermark.data.file_mover"

#def _create_module_log():
 #s   return logger.log2stdout(module_name)

def main_parser():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i", "--inputlogpath", dest="inputlogpath", default=None, help=r"input log path")
    parser.add_option("-o", "--outputpath", dest="outputpath", default=None, help=r"out log path")
    return parser

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')     # <! 中文设置
    #logger.g_logger = _create_module_log()

    #get opt
    parser = main_parser()
    (opt, args) = parser.parse_args()
    #logger.g_logger.info("********* start ********")


    fileFullPathList = []
    fileNameList = []
    pathDir = os.listdir(opt.inputlogpath)
    for allDir in pathDir:
        if allDir == ".DS_Store":
            continue
        childdir = os.path.join('%s/%s' % (opt.inputlogpath, allDir))

        inner_pathDir = os.listdir(childdir)
        for inner_allDir in inner_pathDir:
            outputFullPath = os.path.join('%s/%s' % (opt.outputpath, inner_allDir))
            inputFullPath = os.path.join('%s/%s' % (childdir, inner_allDir))
            shutil.move(inputFullPath, outputFullPath)
