# alist 自动追番脚本
简单的追番脚本，使用rclone+alist+qbit实现自动追番
不需要大盘鸡，只要能放得下1集就能追完全集，实测4g硬盘nat鸡追完2023.4到2023.10的所有番

## 简单功能说明 (详情见代码注释)
ani.py : 用于自动添加订阅
auto.sh : 用于上传视频至网盘，可选择吸血或做种(默认做种)，需在qbit设置--torrent 完成时运行外部程序添加 `bash /root/auto.sh "%N" "%F" "%R" "%D" "%C" "%Z" "%I"` ，其中/root/auto.sh换为脚本实际路径
md.sh : 用于添加最近更新详情，方便看番
qb_del.py ： 用于批量删除过期订阅和本地目录，慎用！
qbclean.sh ： 清理堆积的qbit日志
