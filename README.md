# 树维教务系统 今日课表 & 天气推送脚本

一个基于 **Python** 的自动化脚本，能够：

1. **登录并抓取** 某高校 EAMS 系统的今日课程  
2. **调用** [和风天气](https://id.qweather.com/) API 获取当日天气  
3. **整合并推送** 上述信息至微信（使用 [WX Pusher](https://wxpusher.zjiecode.com/)）

---

## 功能亮点

- ✨ **自动登录**：模拟浏览器行为，可以用于抢课等其他功能，欢迎二开。
- 📋 **课程美化**：格式化输出课程名、上课时间与教室  
- ⛅ **实时天气**：集成和风天气，支持城市/经纬度查询  
- 🚀 **微信推送**：无感知地将消息推至指定 UID 或 Topic  
- ⏰ **定时任务**：配合 `cron`、Windows 任务计划等工具定时运行  

---

## 目录

- [前置条件](#前置条件)  
- [安装](#安装)  
- [配置](#配置)  
- [用法](#用法)  
- [定时执行](#定时执行)  
- [项目结构](#项目结构)  
- [贡献](#贡献)  
- [许可证](#许可证)  

---

## 前置条件

| 依赖           | 版本   | 说明                   |
| -------------- | ------ | ---------------------- |
| Python         | ≥ 3.7  | 建议使用 3.10+         |
| requests       | Latest | 网络请求               |
| beautifulsoup4 | Latest | 解析 HTML              |
| pycryptodome   | Latest | 可选：更复杂的加密登陆 |

一次性安装：

```bash
pip install -r requirements.txt
```

## 安装

```bash
# 克隆仓库
git clone https://github.com/1848431227/shuwei-eams-schedule-push.git
cd shuwei-eams-schedule-push

# 安装依赖
pip install -r requirements.txt
```

------

## 配置

在项目根目录**创建 `.env` 文件**（或直接使用环境变量）并填写：

| 变量                  | 说明                            |
| --------------------- | ------------------------------- |
| `EAMS_USERNAME`       | EAMS 登陆用户名                 |
| `EAMS_PASSWORD`       | EAMS 登陆密码（明文或自行加密） |
| `QWEATHER_API_KEY`    | 和风天气 API Key                |
| `QWEATHER_API_SECRET` | 可选：和风天气密钥              |
| `WXPUSHER_APP_TOKEN`  | WX Pusher AppToken              |
| `WXPUSHER_TOPIC_ID`   | WX Pusher Topic ID              |
| `WXPUSHER_UID`        | 可选：指定推送目标 UID          |

**示例 `.env`**：

```dotenv
EAMS_USERNAME=your_username
EAMS_PASSWORD=your_password
QWEATHER_API_KEY=your_qweather_key
QWEATHER_API_SECRET=your_qweather_secret
WXPUSHER_APP_TOKEN=your_wxpusher_token
WXPUSHER_TOPIC_ID=your_topic_id
WXPUSHER_UID=optional_user_uid
```

------

## 用法

```bash
python main.py
```

脚本流程：

1. 登录 EAMS，抓取并解析**今日课表**
2. 调用和风天气 API，获取**今日天气**
3. 组合文本消息
4. 通过 WX Pusher **推送至微信**

**终端示例输出**

```
✅ 登录成功！
===== 今日课表 =====
【第1节课】
课程: 高数（一）
时间: 08:20-10:00
地点: 东实验楼101

【第2节课】
课程: 线性代数
时间: 10:15-12:00
地点: 东实验楼203

==== 今日天气 ====
北京 · 晴  最高 25℃ / 最低 15℃
空气质量：良

消息已推送至微信 ✔
```

------

## 定时执行

### Linux / macOS（cron）

```bash
# 每天 07:30 运行
30 7 * * * cd /path/to/eams-weather-push && /usr/bin/python3 main.py >> run.log 2>&1
```

### Windows（任务计划）

1. 触发器：每日 07:30
2. 操作：启动程序
   - **程序**：`python.exe`
   - **参数**：`C:\path\to\main.py`
   - **起始于**：`C:\path\to\eams-weather-push`

------

## 贡献

欢迎 Issue / PR！

------

## 许可证

本项目使用 **MIT License** 发布，详见 [LICENSE](https://chatgpt.com/LICENSE)。

------

> **补充说明**
>
> - 如果不想使用 `.env`，可在源码中硬编码凭证，但务必避免泄露。
> - 在这个基础上进行二开的请标注本仓库为源头
> - 如需借鉴我的登录方式，请标注本仓库为源头

