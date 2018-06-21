import numpy as np
import math

def rectTranslate(inputrect, xs, ys):
    inputrect = ((int(inputrect[0][0] + xs), int(inputrect[0][1] + ys)), (int(inputrect[1][0] + xs), int(inputrect[1][1] + ys)))
    return inputrect

def rect_scale(inputrect, scale):
    scaled_rect = ((int(inputrect[0][0] * scale), int(inputrect[0][1] * scale)), (int(inputrect[1][0] * scale), int(inputrect[1][1] * scale)))
    return scaled_rect

def rectScale(inputrect, scaleY, scaleX):
    scaled_rect = ((int(inputrect[0][0] * scaleX), int(inputrect[0][1] * scaleY)), (int(inputrect[1][0] * scaleX), int(inputrect[1][1] * scaleY)))
    return scaled_rect

def clamp(val, vmin, vmax):
    if val < vmin:
        return vmin
    if val > vmax:
        return vmax
    return val

def rectClamp(inputrect, wmin, wmax, hmin, hmax):
    inputrect = ((clamp(inputrect[0][0], wmin, wmax), clamp(inputrect[0][1], hmin, hmax)), (clamp(inputrect[1][0], wmin, wmax), clamp(inputrect[1][1], hmin, hmax)))
    return inputrect

def aver(loc, loc_len):
    loc_average = int(sum(i for i in loc) / loc_len)
    return loc_average


def calRectWidthAndHeight(rect):
    width = rect[1][0] - rect[0][0]
    height = rect[1][1] - rect[0][1]
    return width, height

def calPointDis(pt1, pt2):
    dx = pt2[0] - pt1[0]
    dy = pt2[1] - pt1[1]
    return  math.sqrt(float(dx * dx + dy * dy))

def rectCenterDis(rect1, rect2):
    w1, h1 = calRectWidthAndHeight(rect1)
    w2, h2 = calRectWidthAndHeight(rect2)
    c1 = (rect1[0][0] + w1 /2, rect1[0][0] + h1 /2)
    c2 = (rect1[0][1] + w2 /2, rect1[0][1] + h2 /2)

    return calPointDis(c1, c2)

def rectRectDis(rect1, rect2):
    w1, h1 = calRectWidthAndHeight(rect1)
    w2, h2 = calRectWidthAndHeight(rect2)
    c1 = (rect1[0][0] + w1 /2, rect1[0][1] + h1 /2)
    c2 = (rect2[0][0] + w2 /2, rect2[0][1] + h2 /2)

    return (calPointDis(c1, c2) + calPointDis((w1, h1), (w2, h2))) / 2

def calAvrageRect(rect_arr, ids):
    x0 = 0
    y0 = 0
    x1 = 0
    y1 = 0
    len_ = len(ids)
    if len == 0:
        return None

    for id in ids:
        x0 = x0 + rect_arr[id][0][0]
        y0 = y0 + rect_arr[id][0][1]

        x1 = x1 + rect_arr[id][1][0]
        y1 = y1 + rect_arr[id][1][1]

    return ((x0 / len_, y0 / len_), (x1 / len_, y1 / len_))

def rectCluster(rect_array):

    len_ = len(rect_array)
    idxs = range(0, len_)
    labels = np.zeros(len_)
    cluster_center = {}
    label = 0
    for i in idxs:
        label = label + 1
        if 0 == labels[i]:
            rect = rect_array[i]
            w, h = calRectWidthAndHeight(rect)
            th =  min(w, h)
            labels[i] = label
            cluster_center[label] = []
            cluster_center[label].append(i)
        else:
            continue

        for j in idxs:
            if 0 == labels[j] and (not i == j):
                tgt_rect = rect_array[j]
                dis = rectRectDis(rect, tgt_rect)
                if dis < th:
                    cluster_center[label].append(j)
                    labels[j] = label

    output_rects = []
    for center_label in cluster_center:
        rect = calAvrageRect(rect_array, cluster_center[center_label])
        output_rects.append(rect)
    if len(output_rects) == 0:
        return None

    return output_rects
