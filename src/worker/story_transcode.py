# -*- coding: UTF-8 -*-
import os, sys
import tool.sys_execute as sys_execute
import config.run_config as run_config
import src.media.transcode as transcode
import tool.logger as logger

module_name = "worker.quality_lab_from_json"

logo1x = 30
logo1y = 30
logo1width = 124
logo1height = 41

logo2x = 184
logo2y = 30
logo2width = 178
logo2height = 43

#trans_parm_base = "-dn -metadata:s rotate= -vcodec libx264 -crf 20 -preset fast -vf \"movie=/Users/yangle/Work/github/trans_codec/key_test/weibo.png,scale=%dx%d[logo0];movie=/Users/yangle/Work/github/trans_codec/key_test/weibo_story_text.png,scale=%dx%d[logo1];[2:v][logo0]overlay=%d:%d[tmp];[tmp][logo1]overlay=%d:%d\" -movflags faststart -x264opts psy=0:ref=5:keyint=90:min-keyint=9:chroma_qp_offset=0:aq_mode=2:threads=36:lookahead-threads=4 -maxrate 2500k -bufsize 5M -async 1 -acodec libfdk_aac -profile:a 4 -b:a 48k -ac 2"
trans_parm_base = "-dn -metadata:s rotate= -vcodec libx264 -crf 20 -preset slow -vf \"movie=/Users/yangle/Work/github/trans_codec/key_test/weibo.png,scale=%dx%d[logo0];[1:v][logo0]overlay=%d:%d\" -movflags faststart -x264opts psy=0:ref=5:keyint=90:min-keyint=9:chroma_qp_offset=0:aq_mode=2:threads=36:lookahead-threads=4 -maxrate 2500k -bufsize 5M -async 1 -acodec libfdk_aac -profile:a 4 -b:a 48k -ac 2"

count = 0


def _create_module_log():
    return logger.log2stdout(module_name)

if __name__ == "__main__":
    logger.g_logger = _create_module_log()
    for img in os.listdir('/Users/yangle/Downloads/我的春晚我的年/3'):
        if os.path.splitext(img)[1] == '.mp4':
            file_path = '/Users/yangle/Downloads/我的春晚我的年/3/' + img
            #path = '-i /Users/yangle/Work/github/trans_codec/key_test/weibo.png -i /Users/yangle/Work/github/trans_codec/key_test/weibo_story_text.png -i /Users/yangle/Downloads/央视上屏素材-微博故事/5/' + img
            path = '-i /Users/yangle/Work/github/trans_codec/key_test/weibo.png -i /Users/yangle/Downloads/我的春晚我的年/3/' + img

            srcInfo = transcode.getStreamInfo(file_path)
            srcWidth = srcInfo.get(u'width', 0)
            ratio = float(srcWidth)/float(720)

            tlogo1x = int(logo1x * float(ratio))
            tlogo1y = int(logo1y * float(ratio))
            tlogo1width = int(logo1width * float(ratio))
            tlogo1height = int(logo1height * float(ratio))

            tlogo2x = int(logo2x * float(ratio))
            tlogo2y = int(logo2y * float(ratio))
            tlogo2width = int(logo2width * float(ratio))
            tlogo2height = int(logo2height * float(ratio))

            #trans_parm = trans_parm_base % (tlogo1width,tlogo1height,tlogo2width,tlogo2height,tlogo1x,tlogo1y,tlogo2x,tlogo2y)
            trans_parm = trans_parm_base % (tlogo1width, tlogo1height, tlogo1x, tlogo1y)

            outputpath = '/Users/yangle/Downloads/video_output/3/' + img
            transcode.transcode(path,outputpath,trans_parm)

            count = count +1
