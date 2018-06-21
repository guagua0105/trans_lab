# coding=utf-8

import cv2
import numpy as np
import os

# 图像二值化
def binary(img_input, val):
    # val=0简单阈值，val=1自适应阈值
    if val == 0:
        ret, img_out = cv2.threshold(img_input, 127, 255, cv2.THRESH_TOZERO)
    elif val == 1:
        img_out = cv2.adaptiveThreshold(img_input, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, 1)
    return img_out


# 计算id水印坐标
def calculate_id_loc(sx, sy, method, logoloc):
    # method：0->最小rec匹配，1calculate_id_loc->最大rec匹配
    # logoloc: 0->leftTop, 1->rightBottom
    sy_offset = sy + 42
    if method == 0:
        sx_offset = sx - 25
        id_rect = ((sx_offset, sy_offset), (sx_offset + 143, sy_offset + 26))
    elif method == 1:
        if logoloc == 0:
            # sx_offset = sx - 2
            sx_offset = 2
        else:
            sx_offset = sx - 100
        id_rect = ((sx_offset, sy_offset), (sx_offset + 218, sy_offset + 28))
    else:
        id_rect = None
    return id_rect

def rect_translate(inputrect, xs, ys):
    inputrect = ((int(inputrect[0][0] + xs), int(inputrect[0][1] + ys)), (int(inputrect[1][0] + xs), int(inputrect[1][1] + ys)))
    return inputrect

def rect_scale(inputrect, scale):
    scaled_rect = ((int(inputrect[0][0] * scale), int(inputrect[0][1] * scale)), (int(inputrect[1][0] * scale), int(inputrect[1][1] * scale)))
    return scaled_rect

def rect_scale(inputrect, scaleY, scaleX):
    scaled_rect = ((int(inputrect[0][0] * scaleX), int(inputrect[0][1] * scaleY)), (int(inputrect[1][0] * scaleX), int(inputrect[1][1] * scaleY)))
    return scaled_rect

def watermark_translate(watermark, xs, ys):
    logo_rect, id_rect = watermark
    logo_rect = rect_translate(logo_rect, xs, ys)
    id_rect = rect_translate(id_rect, xs, ys)
    watermark = (logo_rect, id_rect)
    return watermark

def watermark_scale(watermark, scale):
    logo_rect, id_rect = watermark
    logo_rect = rect_scale(logo_rect, scale)
    id_rect = rect_scale(id_rect, scale)
    watermark = (logo_rect, id_rect)
    return watermark

def watermark_scale(watermark, scaleY, scaleX):
    logo_rect, id_rect = watermark
    logo_rect = rect_scale(logo_rect, scaleY, scaleX)
    id_rect = rect_scale(id_rect, scaleY, scaleX)
    watermark = (logo_rect, id_rect)
    return watermark

def clamp(val, vmin, vmax):
    if val < vmin:
        return vmin
    if val > vmax:
        return vmax
    return val

def rect_clamp(inputrect, wmin, wmax, hmin, hmax):
    inputrect = ((clamp(inputrect[0][0], wmin, wmax), clamp(inputrect[0][1], hmin, hmax)), (clamp(inputrect[1][0], wmin, wmax), clamp(inputrect[1][1], hmin, hmax)))
    return inputrect

def watermark_clamp(watermark, wmin, wmax, hmin, hmax):
    logo_rect, id_rect = watermark
    logo_rect = rect_clamp(logo_rect, wmin, wmax, hmin, hmax)
    id_rect = rect_clamp(id_rect, wmin, wmax, hmin, hmax)
    watermark = (logo_rect, id_rect)
    return watermark

def ROI_detect(img_ori, img_flag):
    xs = 0
    xe = img_ori.shape[1]
    ys = 0
    ye = img_ori.shape[0]

    #if ye < xe or abs(float(ye) / xe - 1.77) > 0.5:
    #    print "not vertical video or not 16:9 video"

    if ye <= 0 or xe <= 0:
        return -1, (None, None)

    result = None
    id_type_flag = 0
    #ROI and preprocess
    if img_flag == 'f':
        xe = img_ori.shape[1] / 2
        ye = img_ori.shape[0] / 2
        roiImg = img_ori[ys:ye, xs:xe]
        id_type_flag = 0


    elif img_flag == 'b':
        xs = img_ori.shape[1] / 2
        xe = img_ori.shape[1]
        ys = img_ori.shape[0] / 2
        ye = img_ori.shape[0]
        roiImg = img_ori[ys:ye, xs:xe]
        id_type_flag = 1


    #detect
    res, watermark = detect(roiImg, id_type_flag)

    #postprocess
    if res == 1:
        if img_flag == 'b':
            watermark = watermark_translate(watermark, xs, ys)
        watermark = watermark_clamp(watermark, 0, img_ori.shape[1], 0, img_ori.shape[0])
    # cv2.rectangle(img_ori, watermark[1][0], watermark[1][1], (7, 249, 151), 2)
    # cv2.imshow('Detected', img_ori)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return res, watermark



# 最大值匹配
def match_img_maxVal(img_input, template, template_w, template_h, flag):
    res = cv2.matchTemplate(img_input, template, cv2.TM_CCOEFF_NORMED)

    [minVal, maxVal, minLoc, maxLoc] = cv2.minMaxLoc(res)
    if maxVal > 0.3:
        result = 1
        loc = maxLoc
        ptx, pty = loc
        target_rect = ((ptx, pty), (ptx + template_w, pty + template_h))
        target_id_rect = calculate_id_loc(ptx, pty, 1, flag)
    else:
        result = 0
        target_rect = (None, None)
        target_id_rect = (None, None)

    # cv2.rectangle(img_input, target_rect[0], target_rect[1], (7, 249, 151), 2)
    # cv2.rectangle(img_input, target_id_rect[0], target_id_rect[1], (7, 249, 151), 2)
    # cv2.imshow('Detected', img_input)
    # # cv2.imwrite('10.jpg',img_rgb)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    rect = (target_rect, target_id_rect)
    return result, rect

def template_init():
    template_binary = [255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,255,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,255,255,255,255,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,255,255,255,255,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,255,0,255,255,255,255,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,0,255,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,255,0,255,255,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,255,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,0,0,255,255,255,255,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,255,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,255,255,0,0,0,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,0,0,255,255,255,255,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,0,0,255,255,255,255,255,0,0,0,0,0,0,0,0,255,255,255,255,255,255,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,255,255,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,0,0,255,255,255,255,255,255,0,0,0,0,0,0,0,255,255,255,255,255,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,255,255,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,0,0,255,255,255,255,255,255,255,255,255,255,0,0,0,0,255,255,255,255,0,0,0,0,255,0,0,255,255,255,255,255,255,0,0,0,255,255,0,0,0,0,0,0,255,0,0,255,255,255,0,0,0,0,255,255,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,255,255,0,0,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,255,255,255,0,0,0,255,255,255,255,255,255,255,255,255,255,255,0,0,255,255,255,255,255,255,255,255,255,0,0,255,255,255,0,0,0,0,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,0,255,255,0,0,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,255,255,0,0,0,255,255,255,255,255,255,255,255,255,255,255,0,0,255,255,255,255,255,255,255,255,255,0,0,255,255,255,0,0,0,0,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,0,0,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,255,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,255,0,0,0,0,0,0,0,255,0,0,255,255,255,0,0,0,0,255,255,0,0,0,0,0,0,0,0,255,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,255,0,0,0,0,255,255,0,0,255,255,0,0,0,255,255,255,255,255,255,255,255,255,0,0,0,255,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,255,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,255,255,0,0,0,0,0,0,0,0,0,0,255,255,255,255,0,0,0,0,0,0,0,0,255,255,255,255,0,0,0,255,255,0,0,255,255,0,0,0,0,255,255,255,255,255,255,255,255,0,0,0,0,255,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,255,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,255,255,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,0,0,0,255,255,0,0,255,255,255,0,0,0,0,0,255,255,0,0,255,255,0,0,0,0,255,255,255,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,255,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,0,0,0,0,0,255,255,255,255,255,0,255,255,255,0,0,0,255,255,0,0,255,255,0,0,0,0,255,255,0,0,0,0,255,255,0,0,0,0,255,255,255,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,255,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,0,0,0,0,0,0,255,255,255,255,0,255,255,255,255,0,0,0,255,255,0,0,255,255,255,0,0,0,255,255,0,255,255,255,255,255,0,0,0,255,255,255,255,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,255,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,255,255,255,255,0,255,255,255,255,255,0,0,0,255,255,0,0,255,255,255,0,0,255,255,0,255,255,255,255,255,255,0,0,0,255,255,0,0,0,0,0,0,255,255,255,0,0,255,0,0,0,255,255,255,255,255,255,255,255,255,0,0,255,255,255,0,0,0,0,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,255,0,255,255,255,255,255,255,255,255,255,255,255,255,0,0,255,255,255,0,0,255,255,0,0,0,0,0,0,0,0,0,0,255,0,0,0,0,0,0,0,255,255,255,255,255,255,0,0,0,255,255,255,255,255,255,255,255,255,0,0,255,255,255,0,0,0,0,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,0,0,255,255,255,0,0,0,0,0,0,0,255,255,0,0,255,255,255,0,0,255,255,0,0,0,0,0,0,0,0,0,0,255,0,0,0,0,0,0,255,255,255,255,255,255,255,0,0,0,255,255,255,255,255,255,255,255,255,0,0,255,255,255,0,0,0,0,255,255,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,255,255,255,255,0,0,0,0,0,255,0,0,0,0,255,255,255,0,255,255,255,0,0,0,0,0,0,0,255,255,255,0,0,255,255,255,0,0,255,255,0,0,0,0,0,0,0,0,0,255,255,0,0,0,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,255,255,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,255,255,255,255,0,0,0,255,255,255,0,0,255,255,255,255,255,0,255,255,0,0,0,0,0,255,255,255,255,255,255,0,0,255,255,255,0,0,255,255,0,0,0,255,255,255,255,255,255,255,255,0,0,0,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,255,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,255,0,0,255,255,255,0,255,0,255,255,0,0,0,255,255,255,0,0,0,255,255,0,0,255,255,255,0,0,255,255,0,0,0,255,255,255,255,255,255,255,255,0,0,0,255,255,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,255,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,0,0,0,255,255,255,0,0,255,255,255,0,0,255,255,0,0,0,0,255,255,255,255,0,0,255,255,0,0,255,255,255,0,0,255,255,0,0,0,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,0,0,0,255,255,255,0,0,255,255,255,0,0,255,255,0,0,255,255,255,0,0,0,0,0,255,255,0,0,255,255,0,0,0,255,255,0,0,0,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,0,0,0,255,255,255,0,0,0,255,255,255,0,255,255,255,0,0,0,255,0,0,0,0,0,255,255,0,0,255,255,0,0,0,255,255,0,0,0,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,255,255,255,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,255,255,255,255,0,0,0,255,255,255,0,0,0,0,255,255,0,255,255,255,255,0,0,255,0,0,0,0,0,255,0,0,0,255,255,0,0,0,255,255,0,0,0,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,255,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,255,255,255,255,0,0,0,255,255,255,0,0,0,255,255,255,255,255,255,255,255,0,0,255,255,255,255,255,255,255,255,0,0,255,255,0,0,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,255,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,255,255,255,255,0,0,0,255,255,255,0,0,0,0,255,255,255,255,255,255,0,255,255,255,255,255,255,255,255,255,0,0,0,255,255,0,0,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,0,0,0,255,255,255,0,0,0,0,0,255,255,255,255,255,0,255,255,255,0,0,0,255,255,0,0,0,255,255,0,0,0,255,255,0,0,0,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,0,0,0,255,255,255,255,0,0,0,0,0,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,255,255,0,0,255,255,255,0,0,0,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,255,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,0,0,0,255,255,255,255,0,0,0,0,0,0,0,255,255,255,255,255,255,255,0,0,0,0,0,255,255,255,0,0,0,255,255,255,0,0,0,255,255,255,255,255,255,255,255,255,0,0,0,255,255,255,255,255,255,0,0,0,0,255,255,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,0,0,0,0,255,255,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,255,255,255,255,0,0,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,255,255,255,255,0,0,0,255,255,255,255,255,255,255,255,255,0,0,0,255,255,255,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,255,0,0,0,0,255,255,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,255,255,255,255,0,0,255,255,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,255,255,255,0,0,0,255,255,255,255,255,255,255,255,255,0,0,0,255,255,255,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,255,255,0,0,0,255,255,255,255,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,255,255,255,255,255,0,0,0,0,0,0,0,255,255,0,0,255,255,0,255,255,255,0,0,0,0,255,255,255,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,0,255,255,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,0,0,0,0,0,0,255,255,255,0,0,0,0,0,0,0,0,0,0,255,255,255,0,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,255,0,255,255,255,255,255,255,255,255,255,255,0,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255]
    template_binary_np = np.array(template_binary, dtype="uint8")
    template_binary_np = template_binary_np.reshape(41, -1)

    return template_binary_np

def template_mark_init():
    template_mark_binary = [255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,255,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,255,255,255,255,0,255,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,255,255,255,255,255,255,255,255,255,255,255,255,0,255,255,255,0,0,0,255,255,255,255,255,255,255,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,255,0,255,255,255,0,0,0,255,255,255,255,255,255,0,255,255,255,255,255,255,255,255,255,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,0,0,255,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,255,255,255,255,255,255,255,255,255,255,255,0,0,255,255,255,0,0,0,255,255,0,0,255,255,255,255,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,0,255,255,255,255,255,255,255,255,255,255,255,255,0,255,255,255,0,0,0,255,255,0,0,255,255,255,255,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,0,255,255,255,255,255,255,255,255,255,255,255,255,0,255,255,255,0,0,0,255,255,0,0,255,255,255,255,255,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,0,255,255,255,255,255,255,255,255,255,255,255,255,0,255,255,255,0,0,0,255,255,0,0,255,255,255,255,255,255,255,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,0,255,255,255,255,255,255,255,0,255,255,255,255,255,0,255,255,0,0,0,255,255,0,0,255,255,255,255,255,255,255,255,0,0,0,0,255,0,0,255,255,255,255,255,255,255,0,255,255,255,255,255,255,255,255,0,0,255,255,255,255,255,255,0,0,0,255,255,0,0,255,255,255,255,255,255,255,255,0,255,0,0,0,0,0,255,255,255,255,255,255,255,0,255,255,255,255,255,255,255,0,0,0,0,0,255,0,0,255,0,0,0,255,255,0,0,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,255,0,0,255,255,255,255,0,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,255,0,0,0,255,255,0,0,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,255,255,0,255,255,255,255,0,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,255,0,0,0,255,255,0,0,255,255,0,0,0,255,255,255,255,255,255,0,255,255,255,255,255,255,255,255,255,255,0,255,255,255,255,0,0,0,0,0,0,0,255,255,255,255,255,0,0,0,255,255,0,0,255,255,0,0,0,0,255,255,255,255,255,0,0,0,255,255,255,0,255,255,255,255,0,255,255,255,255,0,0,0,0,0,255,255,255,255,255,255,255,0,0,0,255,255,0,0,255,255,255,0,0,0,0,0,0,255,0,0,0,0,255,255,0,0,255,255,255,255,0,255,255,0,0,0,0,0,0,255,255,255,0,0,0,255,255,0,0,0,255,255,0,0,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,0,255,255,255,255,0,0,255,255,255,0,0,255,255,255,255,0,0,255,255,255,255,0,0,0,0,255,0,0,255,255,255,0,0,0,255,255,0,0,255,0,0,0,0,255,255,0,255,255,255,255,0,0,255,255,255,0,0,255,255,0,0,0,255,255,255,255,255,255,255,255,255,255,0,0,255,255,255,0,0,0,255,255,255,255,255,0,255,255,255,255,255,255,255,255,255,255,0,0,255,255,255,0,0,0,0,0,255,255,255,255,255,255,255,255,0,0,255,255,0,0,255,255,255,0,0,0,255,255,255,255,255,255,255,255,0,255,255,255,255,255,255,255,0,0,255,0,0,0,0,255,0,0,255,255,255,0,0,0,0,0,0,0,255,255,0,0,255,255,255,0,0,0,255,255,0,0,255,255,0,255,0,255,255,0,255,255,255,255,0,0,0,0,0,255,255,255,0,255,255,255,0,0,0,0,0,0,0,0,255,255,0,0,255,255,255,0,0,0,255,255,0,0,0,255,255,255,0,255,255,255,255,255,255,255,0,0,0,0,0,255,255,255,0,255,255,0,0,0,0,0,255,0,0,0,255,255,0,0,255,255,255,0,0,0,255,255,255,255,0,255,255,255,255,255,255,255,255,255,255,255,0,0,255,0,255,255,0,255,0,255,255,0,0,0,255,255,255,0,0,255,255,255,0,0,255,255,255,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,255,255,0,0,255,255,0,0,0,0,255,255,255,0,0,0,255,255,0,0,255,255,255,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,255,255,0,0,255,255,0,0,255,255,255,255,255,0,0,0,255,255,0,0,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,255,255,0,0,255,255,255,0,0,0,0,0,0,0,0,0,255,255,0,0,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,255,255,0,0,255,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,255,0,0,0,255,255,255,255,0,0,0,0,255,255,255,255,255,255,0,0,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,255,255,255,0,255,255,255,0,0,255,255,255,255,0,0,0,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,255,255,255,0,255,255,0,0,0,0,255,255,0,0,0,255,255,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,255,255,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,255,0,0,0,0,255,255,255,255,255,255,255,255,0,0,0,0,0,255,255,255,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,255,0,255,255,255,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,255,0,0,255,255,255,255,255,255,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,255,255,0,0,0,0,255,255,255,255,255,255,255,255,0,0,0,255,255,255,255,255,0,0,0,0,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,0,0,255,255,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,255,0,0,255,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,0,0,0,0,0,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255,255]
    template_mark_binary_np = np.array(template_mark_binary, dtype="uint8")
    template_mark_binary_np = template_mark_binary_np.reshape(48, -1)
    return template_mark_binary_np

def detect_debug(image_path, template_path, flag):
    # img_rgb = cv2.imread(image_path)
    img_gray = cv2.cvtColor(image_path, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(template_path, 0)
    img_binary = binary(img_gray, 1)
    template_binary = binary(template, 1)

    # template_binary_id = template_binary.reshape(1, -1)
    # np.savetxt("/Users/liuwen/Downloads/douyin/template_2_3.txt", template_binary_id, fmt="%d", delimiter=",")


    result = match_img_maxVal(img_binary, template_binary, flag)

    return result


def detect(img_rgb, flag):
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    img_binary = binary(img_gray, 1)
    template_binary = template_init()

    result = match_img_maxVal(img_binary, template_binary, template_binary.shape[1], template_binary.shape[0], flag)
    if result[0] == 0:
        # template_mark = cv2.imread('/Users/liuwen/Downloads/douyin/template_2_3_mark.bmp', 0)
        #
        # template_binary_mark = binary(template_mark, 1)
        #
        # template_binary_id = template_binary_mark.reshape(1, -1)
        # np.savetxt("/Users/liuwen/Downloads/douyin/template_2_3_mark.txt", template_binary_id, fmt="%d", delimiter=",")
        template_binary_mark = template_mark_init()
        result = match_img_maxVal(img_binary, template_binary_mark, template_binary.shape[1] + 10, template_binary.shape[0], flag)
    # print result
    # cv2.rectangle(img_rgb,result[1][0][0], result[1][0][1], (7, 249, 151), 2)
    # cv2.imshow('Detected', img_rgb)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return result


def aver(loc, loc_len):
    loc_average = int(sum(i for i in loc) / loc_len)
    return loc_average


def detectWaterMarkSingleVideo(sampleFolderPath, sampleImageFullPathes, sampleImageNames, minSuccessDetectRate=0.4, openDebug=True):
    resultString = []
    id = 0

    invalideFileCount = 0

    front_sample_count = 0
    front_detected_count = 0
    back_sample_count = 0
    back_detected_count = 0

    logo_front_x = []
    logo_front_y = []
    logo_back_x = []
    logo_back_y = []

    for sn in sampleImageNames:
        imagePath = sampleImageFullPathes[id]

        if not os.path.isfile(imagePath):
            invalideFileCount = invalideFileCount + 1
            id = id + 1
            continue

        img = cv2.imread(imagePath)

        result, (logo_rect, id_rect) = ROI_detect(img, sn[0])

        if result == 1:
            if sn[0] == 'f':
                logo_front_x.append(logo_rect[0][0])
                logo_front_y.append(logo_rect[0][1])
                front_detected_count = front_detected_count + 1

            elif sn[0] == 'b':
                logo_back_x.append(logo_rect[0][0])
                logo_back_y.append(logo_rect[0][1])
                back_detected_count = back_detected_count + 1

            if openDebug:
              if not os.path.exists(sampleFolderPath + "/1suc/"):
                  os.mkdir(sampleFolderPath + "/1suc/")

              resImgPath = sampleFolderPath + "/1suc/" + str(result) + sn

              cv2.rectangle(img, logo_rect[0], logo_rect[1], 255, 2)
              cv2.rectangle(img, id_rect[0], id_rect[1], 255, 2)
              cv2.imwrite(resImgPath, img)
              # plt.imshow(img)
              # plt.show();
        else:
            if openDebug:
              resultString.append(sn + ": " + "result: " + str(result) + "\n")

        if not result < 0:
            if sn[0] == 'f':
                front_sample_count = front_sample_count + 1
            elif sn[0] == 'b':
                back_sample_count = back_sample_count + 1

        id = id + 1

    front_detected_success_rate = 0.0
    if front_sample_count > 0:
        front_detected_success_rate = float(front_detected_count) / front_sample_count
    back_detected_success_rate = 0.0
    if back_sample_count > 0:
        back_detected_success_rate = float(back_detected_count) / back_sample_count

    # logging.debug("[%s]front_detected_success_rate = %f = %d/%d; back_detected_success_rate = %f = %d/%d",sampleFolderPath, front_detected_success_rate, front_detected_count, front_sample_count, back_detected_success_rate, back_detected_count, back_sample_count)

    if openDebug and len(resultString) > 0:
        if not os.path.exists(sampleFolderPath + "/0fal/"):
            os.mkdir(sampleFolderPath + "/0fal/")

        sampleFolderPath = sampleFolderPath + "/0fal/" + "res.txt"
        f = open(sampleFolderPath, "w")
        for line in resultString:
            f.write(line)
        f.close()

    watermark_detected = 0
    watermark_rect = []
    if front_detected_success_rate >= minSuccessDetectRate:
        (fx, fy) = (aver(logo_front_x, front_detected_count), aver(logo_front_y, front_detected_count))
        f_logo_rect = ((fx, fy), (fx + 113, fy + 41))  # logo rect
        f_id_rect = calculate_id_loc(fx, fy, 1, 0)  # id position calculate

        rect_front = [f_logo_rect, f_id_rect]
        watermark_rect.append(rect_front)
        watermark_detected = watermark_detected + 1

    if back_detected_success_rate >= minSuccessDetectRate:
        (bx, by) = (aver(logo_back_x, back_detected_count), aver(logo_back_y, back_detected_count))
        b_rect = ((bx, by), (bx + 113, by + 41))
        b_id_rect = calculate_id_loc(bx, by, 1, 1)
        rect_back = [b_rect, b_id_rect]
        watermark_rect.append(rect_back)
        watermark_detected = watermark_detected + 1


    return watermark_detected, watermark_rect

