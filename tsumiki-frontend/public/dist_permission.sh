#!/bin/bash

# 给目录及其子目录添加 rx（进入+读取列表）权限
# chmod -R o+rx /var/www/tsumiki/tsumiki-frontend/dist
# 给文件添加 r（读取）权限（目录已有 rx，文件只需要 r）
# chmod -R o+r /var/www/tsumiki/tsumiki-frontend/dist

# 更简洁的方式（因为 +X 只会给目录加执行权限，不会给普通文件加）
chmod -R o+rX /var/www/tsumiki/tsumiki-frontend/dist

echo "fix permission finished"