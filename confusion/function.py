#!/usr/bin/python
#coding:utf-8
import os, json, time
from time import strftime, localtime
import sys
import re
import paths
#系统库路径
sys_root_path = "/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk/System/Library/Frameworks"
#主工程路径
rootpath=os.getcwd()+"/"
root_path = rootpath+paths.name
#pod路径
pod_root_path = rootpath+"Pods"

ignore_files = []

read_h_file_method = False
#所有文件的属性名 格式为一个文件名对应所有属性 {file_name:[attributes]}
all_file_attributes = {}
all_file_h_methods = []
all_file_ignore_methods = []
all_file_ignore_manual_method = ['(void)setFrame:', '(void)setHeight:', '(void)setWidth:', '(void)setCurrentPage:',
                                 '(instancetype)sharedCoreDataManager', "(void)setLastUpdatedTimeKey:",  "(void)setIsEmpty:",
                                 '(void)ptzButtonClick:','(void)longPressPTZButtonClick:','(void)cancelPTZButtonActionClick:',
                                 '(Class)layerClass','(UIView *)addPrivilegeViewInView:','(NSTimer *)countDownTimer','(UIView *)addChooseViewWithY:',
                                 '(UIButton *)addPayButtonInView:','(UIView *)addRecordMathodWithY:'
                                 ]
method_prefix = sys.argv[1]+"_"


def modify_file_mothod_with_path(path: str):
    # 过滤分类方法 暂时不处理分类方法
    is_category = path.__contains__("+")
    if is_category:
        return

    file_methods = get_method_with_file(path)
    print("file_method -------", file_methods)
    prefix_file_methods = add_methon_prefix_with_methods(file_methods)

    # for method_dic in prefix_file_methods:
    #     print(method_dic)

    with open(path, "r+") as class_file:
        new_file_str = ""
        for lineIdx, line in enumerate(class_file):

            new_file_str += modify_line(line, prefix_file_methods)
        # 写入文件
        class_file.seek(0)
        class_file.write(new_file_str)

def get_method_with_file(path:str):
    file_methods = []
    file_name = get_file_name_with_path(path)
    get_attribute_with_path(path)
    attribute_array = all_file_attributes[file_name]
    with open(path, "r+") as class_file:
        # "re.S"
        # content = re.findall("\s*[-+]\s*\(.*\).*[;{]", file_str)
        for lineIdx, line in enumerate(class_file):
            # if content.__contains__("")
            content = re.findall("^\s*[-+].*[;{]", line)
            if len(content) > 0:
                # print(content[0])
                # 去除开头- + 结尾; { 字符
                method_str = re.sub("[-+;{]", "", content[0]).strip()
                ignore = False
                if method_str.__contains__("IBAction"):
                    continue
                for method in file_methods:
                    if method_str == method:
                       ignore = True
                       break
                if ignore:
                    print("重复的方法 --- %s" % method_str)
                    continue
                # 忽略 开头为initWith方法
                method_context = re.search("\).*?:|\).*", method_str)
                if method_context is None:
                    continue
                method_name = method_context.group().replace(")", "").strip()
                method_result = re.match("initWith", method_name)
                if method_result is not None:
                    ignore = True
                if ignore:
                    print("忽略的initWith方法 --- %s" % method_str)
                    continue
                #忽略属性方法
                for attribute_str in attribute_array:
                    ignore = same_method_with_attribute(attribute_str, method_str)
                    if ignore:
                        print("忽略的方法 --- %s" % method_str)
                        break
                if ignore:
                    continue
                #忽略系统,pod,SDK的方法
                for ignore_method in all_file_ignore_methods:
                    ignore = same_method_with_ignore(method_str, ignore_method)
                    if ignore:
                       print("忽略的方法2 --- %s" % method_str)
                       break
                if ignore:
                   continue
                #忽略自定义的方法
                for ignore_custom_method in all_file_ignore_manual_method:
                    ignore = same_method_with_ignore(method_str, ignore_custom_method)
                    if ignore:
                        print("忽略自定义的方法 --- %s" % method_str)
                        break
                if ignore:
                   continue
                file_methods.append(method_str)
    return file_methods

#替换每行
def modify_line(line: str, methods: list):
    #过滤属性
    result = re.findall('\s*@property|\s*@interface|\s*@implementation|\s*@end|\s*#import|\s*@protocol|\s*@class', line)
    if len(result) != 0 or line == "\n" or len(line) <= 5 or "super" in line:
        return line
    new_line = line
    for method_dic in methods:
        for key in method_dic:
            # 去除 方法为 getVideoUrl , getVideoUrl: 替换时,将后者覆盖的情况
            if not line.__contains__("%s:" % key):
                if line.__contains__(key):
                    new_line = re.sub(r"%s" % key, method_dic[key], new_line)
            else:
                print("被过滤的行 ---", line)
    return new_line


#只修改方法的第一个名称,增加前缀  生成新的方法数组
def add_methon_prefix_with_methods(ori_methods: list):
    target_methods = []
    for ori_method in ori_methods:
        # print(ori_method)
        method_context = re.search("\).*?:|\).*", ori_method)
        if method_context is None:
            continue
        method_name = method_context.group().replace(")", "")
        # print(method_params)
        new_method_name = method_prefix + method_name
        method_dic = {method_name: new_method_name}
        ignore = False
        for method_dic_info in target_methods:
            if method_name in method_dic_info:
              ignore = True
              print("忽略的重复方法" + ori_method)
              break
        if ignore:
            continue
        target_methods.append(method_dic)
    return target_methods


#获取文件的属性
def get_attribute_with_path(path: str):
    file_name = get_file_name_with_path(path)
    #将.h .m的属性记录
    attributes = []
    for key in all_file_attributes:
        if key == file_name:
           attributes = all_file_attributes[file_name]

    with open(path, "r+") as class_file:
        for lineIdx, line in enumerate(class_file):
            content = re.findall("^\s*@property.*;", line)
            if len(content) > 0:
                # 获取属性名字
                #.split(")").pop().strip() 复杂如同 NSArray <WYCameraToolBarItem *> *dataSource
                attribute_str = re.search("\).*;", content[0]).group()
                attribute_str = re.sub("[\);]", "", attribute_str).strip()
                attributes.append(attribute_str)
    all_file_attributes[file_name] = attributes
    # print(all_file_attributes)

#获取文件名
def get_file_name_with_path(path: str):
    return path.split("/").pop().split(".")[0]

#获取set方法
def get_set_method_with_attribute(attribute: str):
    # 只替换一次
    return "set" + attribute.replace(attribute[0], attribute[0].upper(), 1)
#获取is方法
def get_is_method_with_attribute(attribute: str):
    return "is" + attribute.replace(attribute[0], attribute[0].upper(), 1)

#判断是否为懒加载方法或者set方法 is方法 例如 声明为getter = isMuted) BOOL muted;这种形式
def same_method_with_attribute(attribute: str, method:str):
    # 分离出属性名
    attr_name = re.split("\*|\s", attribute).pop()
    # print("att_name  ---- " + attr_name)
    #判断method 是否有多个参数 用: 分割判断
    if len(method.split(":")) > 2:
        return False
    set_attr_method = get_set_method_with_attribute(attr_name)
    # print("set Method ----- ", set_attr_method)
    is_attr_method = get_is_method_with_attribute(attr_name)

    method_content = re.search("\).*?:|\).*", method)
    if method_content is None:
        return False
    method_name = method_content.group().replace(")", "").strip().split(" ")[0].replace(":", "")

    if set_attr_method == method_name or attr_name == method_name or is_attr_method == method_name:
        return True
    return False
#判断是否为需要忽略的方法
def same_method_with_ignore(method: str, ignore_method:str):
    #类似++i;这种语句
    method_content = re.search("\).*?:|\).*", method)
    if method_content is None:
        return False
    method_name = method_content.group().replace(")", "").strip().split(" ")[0]
    # print("ignore_method ----" + ignore_method)
    # 存在 If the specified asset is an instance of AVComposition, the renderSize will be set to the naturalSize of the AVCompositio 方法
    ignore_method_content = re.search("\).*?:|\).*", ignore_method)
    if ignore_method_content is None:
        return False
    ignore_method_name = ignore_method_content.group().replace(")", "").strip().split(" ")[0]
    if ignore_method_name.__contains__(method_name):
        return True
    else:
        return False


#所有需要忽略的方法名称 如系统方法 pod里的方法
def get_all_ignore_method(path: str):
    for dirpath, dirname, filenames in os.walk(path):
        # 屏蔽SDK,.h文件
        # "Meari/SDK" in dirpath or
        if "Frameworks/PDFKit" in dirpath or "Frameworks/vImage" in dirpath:
            continue
        for filename in filenames:
            if ".h" in filename:
                filePath = os.path.join(dirpath, filename)
                print("filePath --- ", filePath)
                with open(filePath, "r", encoding="utf8", errors="ignore") as f:
                    # print(filePath,dirpath)
                    for lineIdx, line in enumerate(f):
                        content = re.findall(r'^\s*[-+].*;', line)
                        if len(content) > 0:
                            # 去除开头- + 结尾; { 字符
                            method_str = re.sub("[-+;{]", "", content[0]).strip()
                            if method_str not in all_file_ignore_methods:
                               all_file_ignore_methods.append(method_str)

    print(all_file_ignore_methods)
    print(len(all_file_ignore_methods))



def run_change_workSpace(path:str):
    for dirpath, dirname, filenames in os.walk(path):
        print(dirpath, dirname, filenames)
        # for filename in filenames:
        if "Meari/Resources" in dirpath:
            continue
        for filename in filenames:
            ignore = False
            for ignore_file in ignore_files:
                if ignore_file == filename:
                   ignore = True
                   break
            if ignore: continue
            if ".m" in filename:
                file_path = os.path.join(dirpath, filename)
                modify_file_mothod_with_path(file_path)

def get_all_h_file_with_workspace(path:str):
    for dirpath, dirname, filenames in os.walk(path):
        print(dirpath, dirname, filenames)
        #or "Meari/SDK" in dirpath
        if "Meari/Resources" in dirpath:
            continue
        if "Meari/SDK/AWS" in dirpath:
            continue
        for filename in filenames:
            ignore = False
            for ignore_file in ignore_files:
                if ignore_file == filename:
                   ignore = True
                   break
            if ignore: continue
            if ".h" in filename:
                file_path = os.path.join(dirpath, filename)

                get_attribute_with_path(file_path)

                with open(file_path, "r", encoding="utf8", errors="ignore") as f:
                    # print(filePath,dirpath)
                    for lineIdx, line in enumerate(f):
                        content = re.findall(r'^\s*[-+].*;', line)
                        if len(content) > 0:
                            # 去除开头- + 结尾; { 字符
                            method_str = re.sub("[-+;{]", "", content[0]).strip()
                            if method_str not in all_file_ignore_methods:
                                all_file_ignore_methods.append(method_str)
    print("all_file_ignore_methods  ========================== ")
    print(all_file_ignore_methods)
    print(len(all_file_ignore_methods))
    print("=================", all_file_attributes)

# 打印当前时间
def printTime():
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()))
    return

start_time = localtime()

#生成忽略方法列表
get_all_ignore_method(sys_root_path)
get_all_ignore_method(pod_root_path)
get_all_h_file_with_workspace(root_path)

#修改工程方法
run_change_workSpace(root_path)

end_time = localtime()

print("startTime -----", strftime("%Y-%m-%d %H:%M:%S", start_time))

print("endTime -----", strftime("%Y-%m-%d %H:%M:%S", end_time))
