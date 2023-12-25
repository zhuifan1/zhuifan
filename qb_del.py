# 用于批量清理qbit过期的下载规则和空文件夹
# 需额外 pip3 install python-dateutil
# 可能误删！！！   慎用！！！  慎用！！！ 
# 需视情况调整第51行的 days=200
# 如果配合仓库内的ani.py则不会误删，还可以将时间调低比如30或60
# 手动添加的其他规则可能误删，根据实际情况调整匹配时间或填入关键词屏蔽

from qbittorrentapi import Client
from datetime import datetime, timedelta
from dateutil import parser
import json
import os
import shutil

# 跳过关键词 不删除包含关键词的规则
keywords = ['关键词一', '关键词二', '关键词三']

# 连接qbit
client = Client(host="localhost:8080", username="admin", password="adminadmin")

# qbit 下载规则路径
# 可输入 sudo find / -type f -name "download_rules.json" 进行查找
file_path = "/root/.config/qBittorrent/rss"  
file_name = "download_rules.json"
rss_rules = os.path.join(file_path, file_name)
rss_dict = {}

# 备份下载规则，若误删手动恢复即可，默认备份路径 /root/qblogs/download_rules.json
backup_dir = "/root/qblogs"
backup_path = os.path.join(backup_dir, file_name)
shutil.copy(rss_rules, backup_path)

# 检查文件是否存在
if os.path.exists(rss_rules):
    with open(rss_rules, encoding="utf8") as f:
        try:
            rss_data = json.load(f)
            rss_dict.update(rss_data)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

# 下载规则及本地目录处理
for title, info in rss_dict.items():
    contains_keyword = any(keyword in title for keyword in keywords)  # 关键词检测
    if contains_keyword:  
        continue
    last_match_str = info.get("lastMatch")  
    if last_match_str:  
        last_match = parser.parse(last_match_str).replace(tzinfo=None)       
        # 检查最后一次匹配是否超过200天
        if (datetime.utcnow() - last_match) > timedelta(days=200):
            savepath = info['savePath']  # 获取对应存放目录
            print(f"番名: {title}")
            print(f"本地存放路径： {savepath}")
            print(f"最后一次更新时间: {info['lastMatch']}")
            # 删除下载规则
            client.rss_remove_rule(rule_name=str(title))
            # 删除本地目录
            if os.path.exists(savepath):
                shutil.rmtree(savepath)
            print("已删除下载规则和本地目录\n")