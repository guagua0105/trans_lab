# coding=utf-8

import cv2
import numpy as np
import os
import fileUtiles
import rectProcess
import templateProcess

def wrapWatermarkRect(matrix, input_pts):

    dst = cv2.perspectiveTransform(input_pts, matrix)
    [[p1], [p2], [p3], [p4]] = np.int32(dst)
    x_leftup = p1[0]
    y_leftup = p1[1]
    x_rightbottom = p3[0]
    y_rightbottom = p3[1]
    if (p1[0] > p2[0]):
        x_leftup = p2[0]
    if (p1[1] > p4[1]):
        y_leftup = p4[1]
    if (p3[0] < p4[0]):
        x_rightbottom = p4[0]
    if (p3[1] < p2[1]):
        y_rightbottom = p2[1]
    target_rect = ((x_leftup, y_leftup), (x_rightbottom, y_rightbottom))
    return target_rect

def wrapWatermarkRectAffine(Maffine, input_pts):
    leftup = np.mat([0, 0, 1]).reshape(3, 1)
    lu = Maffine * leftup
    rightbottom = np.mat([input_pts[2][0][0], input_pts[2][0][1], 1]).reshape((3, 1))
    rb = Maffine * rightbottom
    [[x_leftup], [y_leftup]] = np.array(lu, 'i')
    [[x_rightbottom], [y_rightbottom]] = np.array(rb, 'i')
    target_rect = ((x_leftup, y_leftup), (x_rightbottom, y_rightbottom))
    return target_rect


def detect_by_fts(template_fts, input_img_fts, template_h, template_w):
    affine = False
    ret, ret_desc, matrix = matching(template_fts, input_img_fts, affine)
    if matrix is None:
        if ret_desc == "success":
            ret_desc = "matrix is None"
        ret = 0

    if ret == 1:
        pts = np.float32([[0, 0], [0, template_h - 1], [template_w - 1, template_h - 1], [template_w - 1, 0]]).reshape(-1, 1, 2)
        if affine:
            watermark = wrapWatermarkRectAffine(matrix, pts)
        else:
            watermark = wrapWatermarkRect(matrix, pts)

    else:
        return 0, ret_desc, None

    return 1, ret_desc, watermark

def matching(tmplate_fts, tgt_img_fts, affine=False):
    kp1 = tmplate_fts[0]
    des1 = tmplate_fts[1]

    kp2 = tgt_img_fts[0]
    des2 = tgt_img_fts[1]

    MIN_MATCH_COUNT = 7
    M = None
    mask = None
    ret = 0
    result_desc = "success"
    if kp1!=[] and len(kp2) > 1:
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)
        # print matches
        good = []
        for m, n in matches:
            if m.distance < 0.5 * n.distance:
                good.append(m)

        if len(good) > MIN_MATCH_COUNT:
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

            if affine:
                M = cv2.estimateRigidTransform(src_pts, dst_pts, 1)
            else:
                M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            ret = 1
        else:
            result_desc =  "Not enough matches are found"
    else:
        result_desc = "No feature is detected!"

    return ret, result_desc, M

def loadTemplate(folderPath, suffix):

    if not folderPath or not suffix:
        return None

    fileFullPathList, fileNameList = fileUtiles.eachFile(folderPath, suffix)
    template_dict = {}
    if suffix[0] == '.':
        suffix = suffix[1:]

    if suffix == '':
        return None

    for fp, fn in zip(fileFullPathList, fileNameList):
        filename, currentSuffix = fileUtiles.getFileNameAndSuffixFromPath(fp)
        if not currentSuffix:
            continue

        if currentSuffix == suffix:
            template_type = filename
            ftdes = templateProcess.retrieve_fts(fp)
            if ftdes:
                template_dict[template_type] = ftdes
    return template_dict

def verifyRect(result_rect, wm_w, wm_h):
    w = result_rect[1][0] - result_rect[0][0]
    h = result_rect[1][1] - result_rect[0][1]
    if w <= 0 or h <= 0:
        return False

    area_ratio = w * h / float(wm_w * wm_h)
    ori_aspect_ratio = wm_w / float(wm_h)
    result_aspect_ration = w / float(h)
    aspect_ratio_diff = abs(ori_aspect_ratio - result_aspect_ration)

    if area_ratio > 0.1 and area_ratio < 4.0 and aspect_ratio_diff < 0.3:
        return True

    return False

def detectWaterMarkSingleVideo(sampleFolderPath, sampleImageFullPathes, sampleImageNames, templateFolderPath, tempalte_suffix, openDebug=True):
    templates = loadTemplate(templateFolderPath, tempalte_suffix)

    template_match_res = {}
    for imagePath, sn in zip(sampleImageFullPathes, sampleImageNames):

        if not os.path.isfile(imagePath):
            continue

        img = cv2.imread(imagePath)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        sift = cv2.xfeatures2d.SIFT_create()
        kps, des = sift.detectAndCompute(img_gray, None)

        final_ret_desc = "success"

        if kps is None or des is None:
            final_ret_desc = "image no ft point"
            continue

        for template in templates:

            result, final_ret_desc, logo_rect = detect_by_fts((templates[template][0], templates[template][1]), (kps, des), templates[template][2], templates[template][3])
            if result == 1:
                if not verifyRect(logo_rect, templates[template][3], templates[template][2]):
                    result = 0

            if result == 1:
                logo_rect = rectProcess.rectClamp(logo_rect, 0, img_gray.shape[1], 0, img_gray.shape[0])

                if not template_match_res.has_key(template):
                    template_match_res[template] = []

                template_match_res[template].append(logo_rect)

                if openDebug:
                  if not os.path.exists(sampleFolderPath + "/1suc/" ):
                      os.mkdir(sampleFolderPath + "/1suc/")

                  if not os.path.exists(sampleFolderPath + "/1suc/" + template + "/"):
                      os.mkdir(sampleFolderPath + "/1suc/" + template + "/")

                  resImgPath = sampleFolderPath + "/1suc/" + template + "/" + str(result) + sn

                  cv2.rectangle(img, logo_rect[0], logo_rect[1], 255, 2)
                  cv2.imwrite(resImgPath, img)

    if openDebug:
        img = cv2.imread(sampleImageFullPathes[0])

        for tmp_name in template_match_res:
            for res in template_match_res[tmp_name]:
                cv2.rectangle(img, res[0], res[1], 255, 2)

        resImgPath = sampleFolderPath + "/1suc/" + sampleImageNames[0]
        cv2.imwrite(resImgPath, img)

    #cluster rect center for every logo
    watermark_detected = 0
    watermark_rect = None

    watermark_rect = {}
    for tmp_name in template_match_res:
        res_array = rectProcess.rectCluster(template_match_res[tmp_name])
        if len(res_array) > 0:
            watermark_rect[tmp_name] = res_array

    if len(watermark_rect) == 0:
        watermark_rect = None
    else:
        watermark_detected = 1
        final_ret_desc = "success"

    return watermark_detected, final_ret_desc, watermark_rect

