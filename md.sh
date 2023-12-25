#!/bin/bash

# 网盘路径
rclone_dest="od"
rclone_path="anime/new"
local_md_path="/root/qblogs/README.MD"

# 获取最近5条日志中的时间和种子名称
result=$(grep -B 1 "种子名称：" /root/qblogs/qb.log | tac | head -n 15 |
  awk -F '删除成功！种子名称:' '{print $1}' | 
  awk -F '[][]' '{print $2, $3, $4, $5}' | tac)

#繁简转化
result=$(echo "$result" | opencc -c t2s.json)

line1="第一条消息 \n"
line2="第二条消息 \n"
line3="第三条消息 \n\n"
line4="**---------------------最近更新---------------------** \n"

# 替换换行符为<br>
result_with_br=$(echo "$result" | awk '{gsub(/\\n/, "<br>"); print}')
line1_br=$(echo "$line1" | awk '{gsub(/\\n/, "<br>"); print}')
line2_br=$(echo "$line2" | awk '{gsub(/\\n/, "<br>"); print}')
line3_br=$(echo "$line3" | awk '{gsub(/\\n/, "<br>"); print}')
line4_br=$(echo "$line4" | awk '{gsub(/\\n/, "<br>"); print}')

# 写入结果到README.MD文件
echo "$line1_br" > $local_md_path
echo "$line2_br" >> $local_md_path
echo "$line3_br" >> $local_md_path
echo "$line4_br" >> $local_md_path
echo "$result_with_br" >> $local_md_path

# 将md文件上传到网盘
rclone delete $rclone_dest:$rclone_path/README.MD
rclone move $local_md_path $rclone_dest:$rclone_path/

