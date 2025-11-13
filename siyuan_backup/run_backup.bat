@echo off
:: 切换到脚本所在目录（替换为你的脚本实际路径）
cd C:\Users\PC\scripts\siyuan_backup
:: 调用 Python 执行脚本（如果系统有多个 Python 版本，建议使用完整路径，如 C:\Python39\python.exe）
python siyuan_backup.py
:: 执行完成后暂停 5 秒（可选，方便调试时查看错误）
timeout /t 5 /nobreak >nul