#!/bin/bash

LOG_FILE="~/qblogs/qb.log"
MAX_SIZE=25 # 设定文件大小，单位为KB
LINES_TO_KEEP=72  # 设定保留行数

# 获取文件大小（单位：KB）
file_size=$(($(stat -c %s "$LOG_FILE") / 1000))

if [ $file_size -gt $MAX_SIZE ]; then
    # 文件大于25KB，保留最后的72行
    tail -n $LINES_TO_KEEP "$LOG_FILE" > "$LOG_FILE.tmp"
    mv "$LOG_FILE.tmp" "$LOG_FILE"
else
    # 文件小于等于25KB，直接退出
    exit
fi
