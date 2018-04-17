# -*- coding: UTF-8 -*-
import json
import config.run_config as run_config
import tool.sys_execute as sys_execute
import shutil
import os
import tool.logger as logger
from abc import abstractmethod

MAX_FRAMES = 600

# -pix_fmt yuv420p -color_range 2 -vf scale=out_color_matrix=bt709,scale=out_range=full -colorspace 1
class QualityWorker():
    @abstractmethod
    def get_score(self, src_video, dst_video, result, show_size, src_offset=(0, 0), dst_offset=(0, 0)):
        raise NotImplementedError

    def parse_vmaf(self, vmaf_result):
        vmafJson = json.loads(open(vmaf_result).read())
        vmafScore = vmafJson["aggregate"]["VMAF_score"]
        os.remove(vmaf_result)
        return vmafScore

    def calc_scaler(self, show_size, srcWidth, srcHeight, dstWidth, dstHeight):
        src_scaler = ""
        dst_scaler = ""
        short_dstName = ""
        if show_size.width > 0:
            # src file scale to show size
            if srcWidth <= show_size.width:  # upsample:cubic
                src_scaler = "-pix_fmt yuv420p -vf scale=%d:%d" % (show_size.width, show_size.height)
                short_dstName = "%dx%dd" % (show_size.width, show_size.height)
            else:
                src_scaler = "-pix_fmt yuv420p -vf scale=%d:%d:flags=gauss" % (show_size.width, show_size.height)
                short_dstName = ".%dx%du" % (show_size.width, show_size.height)
            # dst file scale to show size
            if dstWidth <= show_size.width:  # upsample:cubic
                dst_scaler = "-pix_fmt yuv420p -vf scale=%d:%d" % (show_size.width, show_size.height)
                short_dstName = "%dx%dd" % (show_size.width, show_size.height)
            else:
                dst_scaler = "-pix_fmt yuv420p -vf scale=%d:%d:flags=gauss" % (show_size.width, show_size.height)
                short_dstName = ".%dx%du" % (show_size.width, show_size.height)
        else:
            # scale to src size
            if srcWidth != dstWidth or srcHeight != dstHeight:
                # to src size
                if srcWidth <= dstWidth:  # upsample:cubic
                    dst_scaler = "-pix_fmt yuv420p -vf scale=%d:%d" % (srcWidth, srcHeight)
                    short_dstName = "%dx%dd" % (srcWidth, srcHeight)
                else:
                    dst_scaler = "-pix_fmt yuv420p -vf scale=%d:%d:flags=gauss" % (srcWidth, srcHeight)
                    short_dstName = ".%dx%du" % (srcWidth, srcHeight)

        return (src_scaler, dst_scaler, short_dstName)


    def preprocess(self, src_video, dst_video, srcInfo, dstInfo, show_size, src_offset=(0, 0), dst_offset=(0, 0)):

        ## set the decode frame number
        srcFrames = srcInfo.get(u'nb_frames', 0)  # convert to int
        dstFrames = dstInfo.get(u'nb_frames', 0)  # convert to int
        if srcFrames > 0:
            decodeFrames = min(srcFrames, MAX_FRAMES)  # decode up to 500 frames
        else:
            decodeFrames = min(dstFrames, MAX_FRAMES)
        logger.g_logger.info("source frame %s dst frams %s decode frame %s" % (srcFrames,dstFrames,decodeFrames))

        srcName = src_video
        dstName = dst_video

        ## scale
        rotate = 0
        if srcInfo.get(u'tags', {}):
            tags = srcInfo.get(u'tags')
            rotate = int(tags.get(u'rotate', 0))

        if rotate / 90 % 2:
            srcWidth = srcInfo.get(u'height', 0)
            srcHeight = srcInfo.get(u'width', 0)
        else:
            srcWidth = srcInfo.get(u'width', 0)
            srcHeight = srcInfo.get(u'height', 0)
        dstWidth = dstInfo.get(u'width', 0)
        dstHeight = dstInfo.get(u'height', 0)
        print srcWidth, srcHeight, dstWidth, dstHeight

        (src_scaler, dst_scaler, short_dstName) = self.calc_scaler(show_size, srcWidth, srcHeight, dstWidth, dstHeight)
        srcYuv = srcName + '.yuv'
        dstYuv = dstName + short_dstName + '.yuv'
        if self.decode(src_video, srcYuv, src_scaler, True, decodeFrames):
            return (False, None, None, 0, 0)
        if self.decode(dst_video, dstYuv, dst_scaler, True, decodeFrames):
            return (False, None, None, 0, 0)

        # offset yuv    (normally useless)
        if src_offset[0] or src_offset[1]:
            srcYuv = self.offset_yuv(srcName, src_offset[0], src_offset[1], srcWidth, srcHeight)
        if dst_offset[0] or dst_offset[1]:
            dstYuv = self.offset_yuv(dstName, dst_offset[0], dst_offset[1], srcWidth, srcHeight)

        return (True, srcYuv, dstYuv, srcWidth, srcHeight)

    # decode yuv
    def decode(self, input_video, output_yuv, scaler="", all_decode=True, frames=0):
        """
        :param input_video:
        :param output_yuv:
        :param scaler:          如需scale，填写参数，如："-vf scale=-2:480 "
        :param all_decode:      是否全部解码
        :param frames:          all_decode为false，解码帧数
        :return:
        """
        if all_decode:
            CMD = "%s -y -i %s -pix_fmt yuv420p %s -vsync 0 %s"
            decodeCmd = CMD % (run_config.ffmpeg, input_video, scaler, output_yuv)
        else:
            CMD = "%s -y -i %s -pix_fmt yuv420p -frames %d %s -vsync 0 %s"
            decodeCmd = CMD % (run_config.ffmpeg, input_video, frames, scaler, output_yuv)
        (returnCode, output) = sys_execute.execute(decodeCmd)
        return returnCode

    # 帧级偏移
    def offset_yuv(self, yuv_name, head, tail, width, height):
        if head or tail:
            orgYuv = yuv_name + '.yuv'
            offsetYuv = yuv_name + '_off.yuv'
            if head:
                with open(orgYuv, 'rb') as in_file:
                    with open(offsetYuv, 'wb') as out_file:
                        out_file.write(in_file.read()[int(width * height * 1.5 * head):])
                print "offset: head", head
            elif tail:
                with open(orgYuv, 'rb') as in_file:
                    with open(offsetYuv, 'wb') as out_file:
                        shutil.copyfileobj(in_file, out_file)
                        out_file.seek(-int(width * height * 1.5 * tail), os.SEEK_END)
                        out_file.truncate()
                print "offset: tail", tail
            os.remove(orgYuv)
            return offsetYuv
        return ''



class VMAFQualityWorker(QualityWorker):
    # execute vmaf cmd
    def vmaf(self, width, height, src_yuv, dst_yuv, vmaf_file):
        CMD = "%s yuv420p %d %d %s %s --out-fmt json > %s"
        vmafCmd = CMD % (run_config.run_vmaf, width, height, src_yuv, dst_yuv, vmaf_file)
        (returnCode, output) = sys_execute.execute(vmafCmd)
        return returnCode

    def get_score(self, src_video, dst_video, srcInfo, dstInfo, result, show_size, src_offset=(0, 0), dst_offset=(0, 0)):
        '''
        :param src_video:
        :param dst_video:
        :param result:
        :param src_offset:  yuv 偏移帧数（头，尾）
        :param dst_offset:
        :return:
        '''

        (returnValue, srcYuv, dstYuv, srcWidth, srcHeight)= self.preprocess(src_video, dst_video, srcInfo, dstInfo, show_size, src_offset, dst_offset)
        if returnValue == False:
            logger.g_logger.error("Failed to process")
            return -1

        # vmaf
        vmafResult = result + '.log'
        if self.vmaf(srcWidth, srcHeight, srcYuv, dstYuv, vmafResult):
            return -2


        # clean
        os.remove(srcYuv)
        os.remove(dstYuv)

        return self.parse_vmaf(vmafResult)



