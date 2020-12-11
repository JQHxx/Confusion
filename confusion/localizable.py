#!/usr/bin/python
#coding:utf-8
import os, paths

path = paths.path

originStr = "1234567890qwertyuiopasdfghjklzxcvbnm"  # 替换前的字符
replaceStr = "0987654321mnbvcxzasdfghjklpoiuytrewq"  # 替换后的字符

# 读取Base.lproj 文件, 获取字符串数组
for dirpath, dirname, filenames in os.walk(path):
    for filename in filenames:
        filePath = os.path.join(dirpath, filename)
        # endName = os.path.splitext(filePath)[1]
        if "Localizable.strings" == os.path.basename(filePath): # 读取Base.lproj 文件
            with open(filePath , "r") as file:
                lines = file.readlines()
            break;

# 获取翻译前后的key map
localDict = {}
for line in lines:
    key = line.split("=")[0].split("\"")[1]
    translateKey = key.translate(str.maketrans(originStr, replaceStr))
    localDict[key] = translateKey

# 替换所有 Localizable.strings 中的 key
for dirpath, dirname, filenames in os.walk(path):
    for filename in filenames:
        filePath = os.path.join(dirpath, filename)
        if "Localizable.strings" == os.path.basename(filePath):
            with open(filePath , "r") as file:
                content = file.read()
            with open(filePath , "w") as file:
                for key in localDict.keys():
                    mb1 = "\"" + key + "\""
                    if mb1 in content:
                        content = content.replace(mb1, "\"" + localDict[key] + "\"")
                file.write(content)

# 替换所有在xcode中使用的 key
for dirpath, dirname, filenames in os.walk(path):
    for filename in filenames:
        filePath = os.path.join(dirpath, filename)
        if filePath.endswith(".h") or filePath.endswith(".m"):
            with open(filePath , "r") as file:
                content = file.read()
            with open(filePath , "w") as file:
                for key in localDict.keys():
                    mb1 = "@\"" + key + "\""
                    if mb1 in content:
                        content = content.replace(mb1, "@\"" + localDict[key] + "\"")
                file.write(content)
