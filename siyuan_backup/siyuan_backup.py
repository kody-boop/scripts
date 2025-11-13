import os
import tempfile
from pathlib import Path
from datetime import datetime
import shutil
from loguru import logger

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError

# 配置日志：仅输出到系统规范的日志目录，不输出到控制台
def get_log_path() -> Path:
    """根据系统获取符合规范的日志存储路径"""
    if os.name == 'nt':  # Windows系统
        # 通常位于 C:\Users\用户名\AppData\Roaming\siyuan_backup\logs
        app_data = Path(os.environ.get('APPDATA', Path.home() / 'AppData' / 'Roaming'))
        log_dir = app_data / 'siyuan_backup' / 'logs'
    elif os.name == 'posix':  # Linux/macOS系统
        if os.geteuid() == 0:  #  root用户
            # Linux: /var/log/siyuan_backup; macOS: /Library/Logs/siyuan_backup
            log_dir = Path('/var/log' if os.path.exists('/var/log') else '/Library/Logs') / 'siyuan_backup'
        else:  # 普通用户
            # Linux/macOS: ~/.local/share/siyuan_backup/logs
            data_dir = Path.home() / '.local' / 'share' / 'siyuan_backup' / 'logs'
            log_dir = data_dir
    else:
        # 未知系统默认到用户目录
        log_dir = Path.home() / '.siyuan_backup' / 'logs'
    
    log_dir.mkdir(parents=True, exist_ok=True)  # 确保目录存在
    return log_dir / 'siyuan_backup.log'

# 移除默认控制台输出，仅添加文件输出
logger.remove()  # 清除默认的控制台处理器
logger.add(
    get_log_path(),
    rotation="1 day",      # 每天轮转
    retention="30 days",   # 保留30天日志
    level="INFO",          # 记录INFO及以上级别
    encoding="utf-8",
    enqueue=True,          # 异步写入避免阻塞
    backtrace=True,        # 记录完整回溯信息
    diagnose=True          # 记录详细诊断信息
)

def get_source_dir() -> Path:
    """跨平台取思源数据目录"""
    source_dir = Path.home() / 'SiYuan' / 'data'
    logger.info(f"思源数据目录: {source_dir}")
    if not source_dir.exists():
        logger.error(f"思源数据目录不存在: {source_dir}")
        raise FileNotFoundError(f"思源数据目录不存在: {source_dir}")
    return source_dir

def zip_dir_to_tmp() -> Path:
    try:
        logger.info("开始创建临时备份目录")
        tmp = Path(tempfile.mkdtemp(prefix='siyuan_backup_'))
        logger.info(f"临时目录创建成功: {tmp}")
        
        time_str = datetime.now().strftime('%Y%m%d-%H%M%S')
        zip_name = f'SiYuan-{time_str}.zip'
        zip_path = tmp / zip_name

        # 复制数据目录到临时目录
        source = tmp / f'data-{time_str}'
        logger.info(f"开始复制数据到临时目录: {source}")
        shutil.copytree(
            get_source_dir(),
            source
        )
        logger.info("数据复制完成")

        # 创建压缩包
        logger.info(f"开始创建压缩包: {zip_path}")
        shutil.make_archive(
            str(zip_path.with_suffix('')),
            'zip',
            str(source.parent),
            str(source.name)          
        )
        logger.info(f"压缩包创建成功，大小: {os.path.getsize(zip_path)/1024/1024:.2f} MB")
        return zip_path
    except Exception as e:
        logger.error(f"创建压缩包失败: {str(e)}", exc_info=True)
        raise

def upload_to_cos(file_path: Path) -> None:
    try:
        # 检查环境变量
        required_vars = ['COS_SECRET_ID', 'COS_SECRET_KEY']
        for var in required_vars:
            if var not in os.environ:
                logger.error(f"环境变量缺失: {var}")
                raise EnvironmentError(f"环境变量缺失: {var}")

        secret_id = os.environ["COS_SECRET_ID"]
        secret_key = os.environ['COS_SECRET_KEY']
        region = 'ap-guangzhou'
        token = None
        config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token)
        client = CosS3Client(config)

        logger.info(f"开始上传文件到COS: {file_path.name}")
        for i in range(3):
            try:
                response = client.upload_file(
                    Bucket='siyuan-backup-1303239686',
                    Key='siyuan_backup/' + file_path.name,
                    LocalFilePath=str(file_path))
                logger.success(f"文件上传成功（第{i+1}次尝试）")
                return
            except (CosClientError, CosServiceError) as e:
                logger.warning(f"第{i+1}次上传失败: {str(e)}")
                if i == 2:
                    logger.error("达到最大重试次数，上传失败")
                    raise
    except Exception as e:
        logger.error(f"COS上传过程出错: {str(e)}", exc_info=True)
        raise

def main():
    logger.info("===== 思源笔记备份程序开始 =====")
    zip_file = None
    try:
        zip_file = zip_dir_to_tmp()
        upload_to_cos(zip_file)
        logger.info("===== 备份程序执行成功 =====")
    except Exception as e:
        logger.error(f"===== 备份程序执行失败: {str(e)} =====")
    finally:
        if zip_file and zip_file.parent.exists():
            logger.info(f"开始清理临时文件: {zip_file.parent}")
            shutil.rmtree(zip_file.parent, ignore_errors=True)
            logger.info("临时文件清理完成")

if __name__ == "__main__":
    main()