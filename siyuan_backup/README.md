# 思源笔记

## 项目介绍
`siyuan_backup` 是一套用于思源笔记（SiYuan）自动备份并上传到腾讯云对象存储（COS）的工具，能够实现思源笔记数据的自动备份、压缩、上传至云端以及临时文件清理等功能，支持 Windows、Linux、macOS 多平台使用。

## 功能特点
- **自动备份**：可自动定位思源笔记默认数据目录，将其打包压缩为带时间戳的 ZIP 包。
- **云端存储**：通过腾讯云 COS SDK 将备份文件上传至指定存储桶，上传失败时支持最多 3 次重试。
- **日志管理**：根据操作系统类型配置日志存储路径，日志按天轮转并保留 30 天，便于问题排查。
- **临时清理**：备份完成后自动删除临时生成的压缩包和目录，节省存储空间。
- **跨平台支持**：适配 Windows、Linux、macOS 系统。

## 文件说明
1. `siyuan_backup.py`：核心 Python 脚本，实现备份的主要逻辑，包括日志配置、数据目录定位、压缩包创建、COS 上传及临时文件清理等。
2. `run_backup.bat`：Windows 批处理脚本，用于切换到脚本所在目录并调用 Python 执行备份脚本，执行完成后暂停 5 秒（方便调试查看错误）。
3. `run_backup.vbs`：Windows 可视化 basic 脚本，用于无窗口运行批处理脚本（隐藏命令行窗口）。
4. `siyuan-backup-example.service`：Linux systemd 服务配置文件示例，用于定义备份服务的运行方式和环境配置。
5. `siyuan-backup-example.timer`：Linux systemd 定时器配置文件示例，用于设置备份任务的执行时间。

## 环境要求
1. 安装 Python 3.x 环境。
2. 安装所需依赖库，可通过以下命令安装：
```bash
pip install loguru qcloud-cos-python-sdk-v5
```
3. 拥有腾讯云 COS 账号，并创建好存储桶，获取 `COS_SECRET_ID` 和 `COS_SECRET_KEY`。

## 配置说明
1. **环境变量配置**：设置腾讯云 COS 相关环境变量
   - `COS_SECRET_ID`：腾讯云账号的 SECRET_ID
   - `COS_SECRET_KEY`：腾讯云账号的 SECRET_KEY
   可通过系统环境变量设置界面进行配置，也可在命令行临时设置（仅当前会话有效）。
2. **脚本路径配置（Windows）**：
   - 编辑 `run_backup.bat` 文件，将 `cd C:\Users\PC\scripts\siyuan_backup` 中的路径替换为实际的脚本所在路径。
   - 编辑 `run_backup.vbs` 文件，将 `objShell.Run "cmd /c C:\Users\PC\scripts\siyuan_backup\run_backup.bat", 0, True` 中的批处理脚本路径替换为实际的 `run_backup.bat` 所在路径。
3. **存储桶配置**：如果需要修改上传的 COS 存储桶，可在 `siyuan_backup.py` 的 `upload_to_cos` 函数中，将 `Bucket='siyuan-1303239686'` 替换为实际的存储桶名称；若需修改存储区域，可修改 `region = 'ap-shanghai'` 为目标区域。

## 使用方法
### 手动运行
1. 确保已完成上述配置。
2. 根据操作系统选择运行方式：
   - Windows：双击 `run_backup.bat` 可在命令行窗口中运行（便于查看输出）；双击 `run_backup.vbs` 可无窗口后台运行。
   - Linux/macOS：在终端中进入脚本所在目录，执行 `python3 siyuan_backup.py` 命令。

### 定时运行（以 Windows 为例）
1. 打开"任务计划程序"。
2. 点击"创建基本任务"，按照向导设置任务名称和描述。
3. 在"触发器"设置中，选择定时触发的时间（如每天、每周等）。
4. 在"操作"设置中，选择"启动程序"，并选择 `run_backup.vbs` 脚本的路径。
5. 完成设置后，任务计划程序将按照设定的时间自动运行备份脚本。

### Linux systemd 服务和定时器（推荐方式）
对于使用 systemd 的 Linux 系统，可以通过配置 systemd service 和 timer 来实现更可靠的定时备份。

1. 复制并重命名服务和定时器文件：
```bash
sudo cp siyuan-backup-example.service /etc/systemd/system/siyuan-backup.service
sudo cp siyuan-backup-example.timer /etc/systemd/system/siyuan-backup.timer
```

2. 编辑服务文件，配置正确的用户、组、工作目录和环境变量：
```bash
sudo nano /etc/systemd/system/siyuan-backup.service
```
   - 修改 `User=` 和 `Group=` 为合适的用户和组
   - 更新 `WorkingDirectory=` 为脚本的实际路径
   - 确认 `ExecStart=` 中的 Python 路径正确
   - 设置真实的 `COS_SECRET_ID` 和 `COS_SECRET_KEY` 环境变量

3. 启用并启动定时器：
```bash
sudo systemctl daemon-reload
sudo systemctl enable siyuan-backup.timer
sudo systemctl start siyuan-backup.timer
```

4. 验证定时器状态：
```bash
systemctl status siyuan-backup.timer
systemctl list-timers | grep siyuan
```

默认配置会在每天凌晨3点执行备份任务。您可以根据需要修改 [Timer] 部分的 OnCalendar 参数来调整执行时间。

## 日志查看
日志文件存储路径根据操作系统不同而有所区别：
- Windows 系统：通常位于 `C:\Users\用户名\AppData\Roaming\siyuan_backup\logs\siyuan_backup.log`
- Linux 系统：root 用户位于 `/var/log/siyuan_backup/siyuan_backup.log`；普通用户位于 `~/.local/share/siyuan_backup/logs/siyuan_backup.log`
- macOS 系统：root 用户位于 `/Library/Logs/siyuan_backup/siyuan_backup.log`；普通用户位于 `~/.local/share/siyuan_backup/logs/siyuan_backup.log`
- 未知系统：默认位于 `~/.siyuan_backup/logs/siyuan_backup.log`

通过查看日志文件，可以了解备份过程中的详细信息，包括成功与否、错误原因等。