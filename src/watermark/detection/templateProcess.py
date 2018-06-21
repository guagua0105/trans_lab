import cv2
import numpy as np
import cPickle

def pickle_keypoints(keypoints, descriptors):
    i = 0
    temp_array = []
    for point in keypoints:
        temp = (point.pt, point.size, point.angle, point.response, point.octave,
        point.class_id, descriptors[i])
        i = i + 1
        temp_array.append(temp)
    return temp_array

def unpickle_keypoints(array):
    keypoints = []
    descriptors = []
    for point in array:
        temp_feature = cv2.KeyPoint(x=point[0][0],y=point[0][1],_size=point[1], _angle=point[2], _response=point[3], _octave=point[4], _class_id=point[5])
        temp_descriptor = point[6]
        keypoints.append(temp_feature)
        descriptors.append(temp_descriptor)
    return keypoints, np.array(descriptors)

def calSIFTFts(image_path):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sift = cv2.xfeatures2d.SIFT_create()
    kps, des = sift.detectAndCompute(img, None)
    return kps, des

def get_and_save_fts(image_gray, output_path):

    sift = cv2.xfeatures2d.SIFT_create()
    kps, des = sift.detectAndCompute(image_gray, None)

    #Store and Retrieve keypoint features
    temp_array = []
    temp = pickle_keypoints(kps, des)
    temp_array.append(temp)
    tplsize = (image_gray.shape[0], image_gray.shape[1])
    temp_array.append(tplsize)
    cPickle.dump(temp_array, open(output_path, "wb"))

def retrieve_fts(fts_path):
    #Retrieve Keypoint Features
    keypoints_database = cPickle.load( open( fts_path, "rb" ) )
    kps, des = unpickle_keypoints(keypoints_database[0])
    return kps, des, keypoints_database[1][0], keypoints_database[1][1]
