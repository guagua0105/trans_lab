# -*- coding: UTF-8 -*-
import config.run_config as run_config
import subprocess

def grab1Pic(input_url, output_fullpath, seek_pos='00:00:03'):

    print ("seek_pos =")
    if not seek_pos:
        return 1

    cmd = ["%s -y -threads 0" % run_config.ffmpeg]
    cmd.append('-i \"%s\"' % input_url)
    cmd.append('-ss %s' % seek_pos)
    cmd.append('-vframes 1')
    cmd.append('%s' % output_fullpath)
    processcmd = ' '.join(cmd)
    print ("ffmpeg cmd =")
    process = subprocess.Popen(processcmd, shell=True)
    process.wait()

    return 0