# 发票申请自动化工具

## 项目介绍

[fapiao](file:///C:/Users/PC/scripts/fapiao/src/gui_main.py#L55-L55) 是一个用于自动化处理发票申请的工具集，主要功能是从Excel文件中读取发票申请数据，通过Selenium自动操作浏览器，在CRM系统中填写并提交发票申请。该工具提供了图形界面和命令行两种使用方式，方便用户根据需求选择。

## 功能特点

- **Excel数据读取**：自动读取指定格式的Excel文件中的发票申请数据
- **浏览器自动化**：使用Selenium自动登录CRM系统并填写发票信息
- **双重操作模式**：提供图形界面和命令行两种操作模式
- **错误处理与记录**：完善的日志记录和错误处理机制，出错时会记录到专门的错误文件中
- **跨平台支持**：支持Windows和Linux系统（根据代码判断）

## 文件说明

1. `src/main.py`：命令行版本的主程序，实现完整的发票申请自动化流程
2. `src/gui_main.py`：图形界面版本的主程序，提供友好的用户界面操作方式
3. `src/read_excel.py`：Excel文件读取模块，负责解析Excel中的发票申请数据
4. `lib/`：存放浏览器驱动程序（如chromedriver）的目录

## 环境要求

1. 安装Python 3.x环境
2. 安装所需依赖库：
   ```bash
   pip install selenium openpyxl loguru python-dotenv pandas
   ```
3. 下载对应系统的ChromeDriver，并放置在`lib`目录下对应子目录中
4. 配置环境变量或创建`.env`文件，设置相关参数

## 配置说明

### 必需配置项

在使用工具之前，需要配置以下环境变量或在项目根目录创建`.env`文件并添加以下内容：

```env
# CRM系统相关配置
CRM_HOME_URL=https://your-crm-system.com/login
CRM_CONTRACT_URL=https://your-crm-system.com/contract-page

# 登录凭证
USER_NAME=your_username
PASSWORD=your_password

# Excel文件路径
EXCEL_PATH=/path/to/your/invoice.xlsx

# 错误记录文件路径（可选，默认保存到桌面）
ERROR_RECORD_PATH=/path/to/error_records.xlsx
```

### Excel文件格式

Excel文件需要满足以下格式要求：

- 工作表名称为"Sheet1"
- 第一行为表头
- 数据从第二行开始，包含合同号、金额、发票内容等相关信息

## 使用方法

### 图形界面模式

```bash
cd src
python gui_main.py
```

运行后会弹出图形界面窗口，可以在界面上配置相关参数并启动处理。

### 命令行模式

```bash
cd src
python main.py
```

直接运行命令行版本，使用预设的配置参数进行处理。

## 注意事项

1. 请确保网络连接稳定，以便能正常访问CRM系统
2. 首次使用时建议使用图形界面模式，方便配置各项参数
3. 请妥善保管登录凭证，不要泄露给他人
4. 如果CRM系统更新了界面元素，可能需要相应调整代码中的元素定位方式
5. 处理过程中不要手动操作浏览器，以免干扰自动化流程

## 日志查看

日志文件会保存在脚本所在目录的`error.log`文件中，可以通过查看日志了解处理过程和排查问题。