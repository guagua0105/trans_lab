import os



def getFileNameAndSuffixFromPath(path):

    if not path:
        return None, None

    if os.path.isdir(path):
        return None, None

    pathSplitted = os.path.split(path)
    filenameWithSuffix = pathSplitted[-1]

    suffix = None
    filename = ''

    if not filenameWithSuffix == '':
        elems = filenameWithSuffix.split('.')
        len_ = len(elems)
        if len_ > 1:
            suffix = elems[-1]
            id = 0
            for e in elems:
                filename = filename + e
                id = id + 1
                if id >= len_-1:
                    break
                else:
                    filename = filename + "."

    if filename == '':
        filename = None

    return filename, suffix

def getFolderNameFormPath(path):
    if not os.path.isdir(path) or not path:
        return None

    if path[-1] == '/':
        path = path[0:-1]

    pathSplitted = os.path.split(path)
    foldername = pathSplitted[-1]
    if foldername == '':
        return None

    return foldername

def eachFolder(filePath):
    fileFullPathList = []
    fileNameList = []
    pathDir = os.listdir(filePath)
    for allDir in pathDir:
        if allDir == ".DS_Store":
            continue
        child = os.path.join('%s/%s' % (filePath, allDir))
        selected = False
        if os.path.isdir(child):
            idx = child.rfind("/")
            if idx > 0:
                folderName = child[idx + 1:]
                selected = True

        if selected:
            fileFullPathList.append(child)
            fileNameList.append(folderName)

    return fileFullPathList, fileNameList

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