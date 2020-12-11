#!/usr/bin/python
#coding:utf-8
import os, paths

path = paths.path
xcodeprojPath = paths.xcodeprojPath

originStr = "1234567890qwertyuiopasdfghjklzxcvbnm"  # 替换前的字符
replaceStr = "0987654321mnbvcxzasdfghjklpoiuytrewq"  # 替换后的字符

# 图片路径数组
imagesetDict = {};  # 新:老 imageset 的名称
gifDict = {}; # gif资源文件
htmlDict = {}; # html资源文件
mp3Dict = {}; # mp3资源文件

# 修改文件夹名称
def renameFolder(filePath):
    imagesetPath = os.path.dirname(filePath)  # imageset路径
    oldBaseName = os.path.basename(imagesetPath).split(".")[0]
    newBaseName = oldBaseName.translate(str.maketrans(originStr, replaceStr))  # 改变后的imageset路径名称 //
    changePath = os.path.dirname(imagesetPath) + "/" + newBaseName + os.path.splitext(imagesetPath)[1]
    os.rename(imagesetPath, changePath)
    # print(oldBaseName, newBaseName, filePath)
    imagesetDict[oldBaseName] = newBaseName  # 保存新老对应的key

# 修改文件名称
def renameFile(filePath):
    oldBaseName = os.path.basename(filePath).split(".")[0]
    newBaseName = oldBaseName.translate(str.maketrans(originStr, replaceStr))  # 改变后的imageset路径名称 //
    changePath = os.path.dirname(filePath) + "/" + newBaseName + "." + \
                 os.path.basename(filePath).split(".")[1]
    if ".gif" in filePath:
        os.rename(filePath, changePath)
        gifDict[oldBaseName] = newBaseName  # 保存新老对应的key
    if ".html" in filePath:
        os.rename(filePath, changePath)
        htmlDict[oldBaseName] = newBaseName
    if ".mp3" in filePath:
        mp3Right = os.path.basename(filePath).split("_")[-1];
        oldBaseName = os.path.basename(filePath).replace("_" + mp3Right, "")
        newBaseName = oldBaseName.translate(str.maketrans(originStr, replaceStr))  # 改变后的imageset路径名称 //
        changePath = os.path.dirname(filePath) + "/" + newBaseName + "_" + mp3Right
        os.rename(filePath, changePath)
        mp3Dict[oldBaseName] = newBaseName


# 修改文件引用
def replaceQuote(oriName, changeName):
    with open(xcodeprojPath, "r") as file:
        str1 = file.read()

    with open(xcodeprojPath, "w") as file:
        str2 = str1.replace(oriName, changeName)
        file.write(str2)

# 遍历修改名称
for dirpath, dirname, filenames in os.walk(path):
    for filename in filenames:
        filePath = os.path.join(dirpath, filename)
        endName = os.path.splitext(filePath)[1]
        if "imageset" in filePath:
            if "Contents.json" in filePath:
                renameFolder(filePath)
        if ".html" == endName or ".gif" == endName or ".mp3" == endName:
            renameFile(filePath)

print(mp3Dict)
# 修改其他需要修改引用资源文件 的引用
for key in gifDict.keys():
    replaceQuote(key + ".gif", gifDict[key] + ".gif")
for key in htmlDict.keys():
    replaceQuote(key + ".html", htmlDict[key] + ".html")
for key in mp3Dict.keys():
    replaceQuote(key, mp3Dict[key])

# 二次遍历 修改图片@2x @3x的名称 和 图片json文件
for dirpath, dirname, filenames in os.walk(path):
    for filename in filenames:
        # print(filePath)
        filePath = os.path.join(dirpath, filename)
        if "imageset" in filePath:
            if "png" in filePath or "jpg" in filePath:  # 找到@2x @3x图片 进行重命名
                imagesetPath = os.path.dirname(filePath)  # 图片路径
                if "@" in os.path.basename(filePath):
                    oldBaseName = os.path.basename(filePath).split("@")[0]
                    newBaseName = os.path.basename(imagesetPath).split(".")[0]  # 新的图片名称
                    changePath = os.path.dirname(filePath) + "/" + newBaseName + "@" + \
                                 os.path.basename(filePath).split("@")[1]
                else:
                    oldBaseName = os.path.basename(filePath).split(".")[0]
                    newBaseName = os.path.basename(imagesetPath).split(".")[0]  # 新的图片名称
                    changePath = os.path.dirname(filePath) + "/" + newBaseName + "." + \
                                 os.path.basename(filePath).split(".")[1]

                contentPath = os.path.dirname(filePath) + "/" + "Contents.json"
                with open(contentPath, "r") as file:  # 读取Contents.json文件
                    contents = file.read()
                with open(contentPath, "w") as file:  # 修改Contents.json文件
                    # print(file, newBaseName, oldBaseName)
                    contents = contents.replace(oldBaseName, newBaseName)
                    file.write(contents)

                os.rename(filePath, changePath)

# 遍历xcode文件工程 ，替换使用资源文件的地方
for dirpath, dirname, filenames in os.walk(path):
    for filename in filenames:
        filePath = os.path.join(dirpath, filename)
        endName = os.path.splitext(filePath)[1]
        if ".h" == endName or ".m" == endName or ".xib" == endName:
            with open(filePath, "r") as file:
                contents = file.read()
            with open(filePath, "w") as file:
                for key in imagesetDict.keys():
                    if key in contents:
                        contents = contents.replace("\"" + key + "\"", "\"" + imagesetDict[key] + "\"")
                for key in gifDict.keys():
                    mb1 = "\"" + key + "\""
                    mb2 = "\"" + key + "."
                    if mb2 in contents:
                        contents = contents.replace(mb2, "\"" + gifDict[key] + ".")
                    elif mb1 in contents:
                        contents = contents.replace(mb1, "\"" + gifDict[key] + "\"")

                for key in htmlDict.keys():
                    mb1 = "\"" + key + "\""
                    mb2 = "\"" + key + "."
                    if mb2 in contents:
                        contents = contents.replace(mb2, "\"" + htmlDict[key] + ".")
                    elif mb1 in contents:
                        contents = contents.replace(mb1, "\"" + htmlDict[key] + "\"")

                for key in mp3Dict.keys():
                    if key in contents:
                        contents = contents.replace(key, mp3Dict[key])


                # print(contents)
                file.write(contents)
