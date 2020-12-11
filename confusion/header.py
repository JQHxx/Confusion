#!/usr/bin/python
#coding:utf-8
import os, keyword, paths

meariPath = paths.path
xcodeprojPath = paths.xcodeprojPath

oldKey = "WY"
newKey = "PG"

# 文件做递归， 拿到有用的.h, .m 文件
path1 = []
for i in os.listdir(meariPath):
    tempPath1 = meariPath + "/" + i
    if "." not in os.path.splitext(i)[0] and "SDK" not in os.path.splitext(i)[0] or "pch" in os.path.splitext(i)[0]:
        path1.append(tempPath1)

tempList = []
def findLastFilePathList(file: list):
    for i in file:
        print(i);
        if os.path.isfile(i):
            if ".h" == os.path.splitext(i)[1] or ".m" == os.path.splitext(i)[1] or ".xib" == os.path.splitext(i)[1] or ".pch" == os.path.splitext(i)[1]:
                # if (os.path.splitext(i)[0].split("/")[-1].startswith(oldKey)) :
                tempList.append(i)
        else:
            tempPath = []
            for j in os.listdir(i):
                tempPath.append(i + "/" + j)
            findLastFilePathList(tempPath)

findLastFilePathList(path1)
# print(tempList)

changeFileDict = {}; #保存改变的文件夹名称, 改变后名称
for i in tempList:
    # 修改文件夹名称
    if os.path.exists(i):
        first = os.path.basename(os.path.dirname(i));
        second = os.path.basename(i).split(".")[0];
        if first in second:  # .h .m xib 文件和文件夹名称重复
            new = first.replace(oldKey, newKey)
            os.rename(os.path.dirname(i),
                      os.path.dirname(os.path.dirname(i)) + "/" + new)
            changeFileDict[first] = first.replace(oldKey, newKey)

for i in tempList:
    index = tempList.index(i);
    for (key, value) in changeFileDict.items():
        if key in i.split("/")[-2] and i.split("/")[-1]:  # 多次处理分类处理
            i = i.replace(key, value, 1)
            tempList[index] = i
            # print(i)
            break;
# print(tempList)

classNameList = []
for i in tempList:
    className = i.split("/")[-1].split(".")[0]
    classNameList.append(className)

for i in tempList:
    with open(i, "r") as file:
        str1 = file.read()
    with open(i, "w") as file:
        for name in classNameList:
            newName = name.replace(oldKey,newKey)
            str1 = str1.replace(name, newName)

        # print(str1)
        file.write(str1)

    # 重命名 .m .h .xib
    oriName = os.path.splitext(i)[0].split("/")[-1];
    changeName = oriName.replace(oldKey, newKey);
    fileName = changeName + os.path.splitext(i)[1]
    os.rename(i, os.path.dirname(i) + "/" + fileName)

    # 修改引用
    with open(xcodeprojPath, "r") as file:
        str1 = file.read()

    with open(xcodeprojPath, "w") as file:
        str2 = str1.replace(oriName, changeName)
        file.write(str2)

