# 自动从nyaa拉取ani的更新并自动创建rss订阅
# 脚本逻辑为检测最近5次更新对应文件夹是否存在，如不存在则创建更新
# 可搭配rclone自动上传网盘脚本，可以让4g硬盘的小鸡追完所有番
# 初次使用必须手动添加ani的rss订阅：https://nyaa.si/?page=rss&u=ANiTorrent 其他都不需要再动

import re
import os
import requests
from qbittorrentapi import Client
from opencc import OpenCC
from datetime import datetime,timedelta
import xml.etree.ElementTree as ET

## 定义关键词屏蔽列表
## 如果有漏网之鱼只需手动删除对应qbit订阅即可，只要不删本地文件夹就不会再更新
keywords = ['中文', '機甲', '超人力霸王', '小不點', '隊長小翼', '限港澳台', '[V2]']

## qbit连接信息
host="localhost:8080"
username="admin"
password="adminadmin"

## 本地固定存放目录 
base_path = "/anime/new"

## 获取ani订阅
def get_ani_subscription():
    url = "https://nyaa.si/?page=rss&u=ANiTorrent"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    r = requests.get(url, headers=headers)
    r.encoding = "utf-8"
    xml_string = r.text
    return xml_string

## qbit添加订阅
def set_qbittorrent_rule(host, username, password, week_qbit, extracted_cht_title , extracted_chs_title):
    client = Client(host=host, username=username, password=password)
    rss_mustcontain_name = extracted_cht_title
    rss_savepath_name = extracted_chs_title
    week_data = week_qbit
    episode_filter = {
        "enabled": True,
        "mustContain": f"{rss_mustcontain_name}",
        "mustNotContain": "限港澳台",
        "useRegex": True,
        "episodeFilter": "",
        "smartFilter": False,
        "previouslyMatchedEpisodes": [],
        "affectedFeeds": [
            "https://nyaa.si/?page=rss&u=ANiTorrent"
        ],
        "ignoreDays": 0,
        "addPaused": False,
        "assignedCategory": "",
        "savePath": f"{base_path}/{week_data}/{rss_savepath_name}"
    }

    client.rss_set_rule(rule_name= f"{rss_savepath_name}", rule_def=episode_filter)

## 订阅处理
def parse_xml_and_process(xml_string, keywords):
    # 解析xml
    root = ET.fromstring(xml_string)
    # 获取channel下的最新5次item 
    items = root.findall(".//channel/item")[:5]

    for item in items:
        # 提取星期 
        pub_date = item.find("pubDate").text  
        date_object = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
        # 凌晨5点前算作昨天(代码中为utc时间，因此判断为21点后为明天)
        if date_object.hour >= 21:
            date_object += timedelta(days=1)
        week_day = date_object.strftime("%a")
        week_mapping = {"Mon": "01", "Tue": "02", "Wed": "03", "Thu": "04", "Fri": "05", "Sat": "06", "Sun": "07"}
        week_qbit = week_mapping.get(week_day)  ## 将星期转化为数字如"01","02"
        contains_keyword = False
        # 提取标题
        title = item.find("title").text 
        contains_keyword = any(keyword in title for keyword in keywords)  # 屏蔽词检测
        if not contains_keyword:
            pattern_with_slash = r'\/(.*?)-\s\d+'
            pattern_without_slash = r'\[ANi\](.*?)-\s\d+'
            # 判断是否存在斜杠
            if '/' in title:
                match_title = re.search(pattern_with_slash, title)
            else:
                match_title = re.search(pattern_without_slash, title)
            if match_title:
                extracted_title = match_title.group(1).strip()  
                if re.search(r'[\[\]\(\)\{\}\.\*\+\?\\\^\$\|]', extracted_title):  # 判断是否存在正则表达式的特殊符号
                    opencc = OpenCC('t2s')  # 繁简体转换
                    extracted_chs_title = opencc.convert(extracted_title) 
                    extracted_cht_title = re.sub(r'([\[\]\(\)\{\}\.\*\+\?\\\^\$\|])', r'\\\1', extracted_title)  # 获取转义后的繁体标题
                else:
                    extracted_cht_title = extracted_title  ## 获取繁体标题(用于qbit关键词过滤)
                    opencc = OpenCC('t2s')   
                    extracted_chs_title = opencc.convert(extracted_title) ## 获取简体标题(用于创建文件夹)
                # 处理订阅  检测指定目录是否已经存在文件夹
                # 如果不存在则创建新的订阅 因此不能删指定目录
                # 目录格式类似 /anime/new/01/番名
                folder_path = f"{base_path}/{week_qbit}/{extracted_chs_title}"
                if not os.path.exists(folder_path):
                    set_qbittorrent_rule(host, username, password, week_qbit, extracted_cht_title , extracted_chs_title)
                    # 在设置规则后创建同名文件夹，确保下次不再触发规则
                    os.makedirs(folder_path)

## 运行函数
xml_result = get_ani_subscription()
parse_xml_and_process(xml_result, keywords)
