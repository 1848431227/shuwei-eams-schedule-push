import requests
import hashlib
import re
import time
import datetime
from bs4 import BeautifulSoup

# 用户信息
USERNAME = "202222222222"
PASSWORD_PLAIN = "202222222222"

# 网站URL
BASE_URL = "http://学校地址"
LOGIN_URL = f"{BASE_URL}/eams/loginExt.action"
HOME_URL = f"{BASE_URL}/eams/homeExt.action"
HOME_MAIN_URL = f"{BASE_URL}/eams/homeExt!main.action"

# WxPusher配置
WXPUSHER_API_URL = "https://wxpusher.zjiecode.com/api/send/message"
APP_TOKEN = "APP_TOKEN"
TOPIC_ID =TOPIC_ID# 用于群发的主题ID

# 和风天气API配置
WEATHER_API_KEY = "天气api"
WEATHER_API_URL = "https://devapi.qweather.com/v7/weather/24h"
# 景德镇艺术职业大学的经纬度坐标（取中点值）
LOCATION = "学校所在经纬度"

# 提取加密前缀
def get_dynamic_prefix(html):
    match = re.search(r"form\['password'\]\.value = CryptoJS\.SHA1\('([a-f0-9\-]+)-'\s*\+\s*form\['password'\]\.value", html)
    if not match:
        match = re.search(r"CryptoJS\.SHA1\('([a-f0-9\-]+)-'\s*\+\s*form\['password'\]\.value", html)
    if match:
        return match.group(1) + "-"
    raise ValueError("❌ 无法提取加密前缀，尝试使用默认值")

# 加密密码
def encrypt_password(prefix, password):
    return hashlib.sha1((prefix + password).encode('utf-8')).hexdigest()

def login():
    # 会话对象
    session = requests.Session()
    
    # 增加随机延迟
    time.sleep(2)
    
    # 访问首页获取cookie
    print("正在访问首页获取Cookie...")
    try:
        session.get(f"{BASE_URL}/eams/")
        time.sleep(2)
    except Exception as e:
        print(f"访问首页出错: {e}")
        return None
    
    # 访问登录页面
    print("正在访问登录页面...")
    resp = session.get(LOGIN_URL)
    print(f"登录页面状态码: {resp.status_code}")
    
    # 尝试从页面中提取前缀
    try:
        prefix = get_dynamic_prefix(resp.text)
        print(f"从页面提取的前缀: {prefix}")
    except ValueError as e:
        print(e)
        # 从登录页面中获取的前缀，实际运行时每次会变化
        prefix = input("请输入登录页面中的前缀 (形如xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx-):")
        if not prefix.endswith("-"):
            prefix += "-"
    
    # 延迟
    time.sleep(3)
    
    # 构造登录数据
    login_data = {
        "username": USERNAME,
        "password": encrypt_password(prefix, PASSWORD_PLAIN),
        "session_locale": "zh_CN"
    }
    
    print(f"用户名: {USERNAME}")
    
    # 伪造浏览器请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": LOGIN_URL,
        "Origin": BASE_URL,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive"
    }
    
    # 提交登录请求
    print("正在提交登录请求...")
    login_resp = session.post(LOGIN_URL, data=login_data, headers=headers)
    print(f"登录请求状态码: {login_resp.status_code}")
    
    # 延迟
    time.sleep(3)
    
    # 访问首页
    print("正在访问首页...")
    home_resp = session.get(HOME_URL)
    print(f"首页请求状态码: {home_resp.status_code}")
    
    # 判断是否成功登录
    if "欢迎" in home_resp.text or "您好" in home_resp.text or "你的名字" in home_resp.text:
        print("✅ 登录成功！")
        return session
    else:
        print("❌ 登录失败")
        return None

def get_homepage_courses(session):
    """直接从首页提取课程信息"""
    if not session:
        print("未登录，无法获取今日课表")
        return
    
    print("\n正在获取首页课表...")
    
    try:
        # 直接访问主页
        main_resp = session.get(HOME_MAIN_URL)
        print(f"首页主内容状态码: {main_resp.status_code}")
        
        # 保存主页内容以便调试
        with open("首页内容.html", "w", encoding="utf-8") as f:
            f.write(main_resp.text)
        print("已保存首页内容为：首页内容.html")
        
        # 从主页解析今日课表
        soup = BeautifulSoup(main_resp.text, 'html.parser')
        
        # 查找今日课程表格
        jrkc_box = soup.find('div', class_='jrkc-box')
        if not jrkc_box:
            print("未找到今日课程信息区域")
            return []
        
        # 提取课程信息
        courses = []
        course_rows = jrkc_box.find_all('tr')
        
        for row in course_rows:
            # 提取时间
            time_td = row.find('td', class_='date')
            time_text = ""
            if time_td:
                # 获取原始文本，保留空白以便处理
                raw_text = time_td.get_text()
                # 使用正则表达式提取开始和结束时间
                time_match = re.search(r'(\d{2}:\d{2}).*?(\d{2}:\d{2})', raw_text, re.DOTALL)
                if time_match:
                    start_time = time_match.group(1)
                    end_time = time_match.group(2)
                    time_text = f"{start_time}-{end_time}"
                else:
                    time_text = re.sub(r'\s+', ' ', raw_text).strip()
            
            # 提取课程名称
            course_name_h5 = row.find('h5')
            course_name = course_name_h5.get_text(strip=True) if course_name_h5 else ""
            
            # 提取地点
            location_span = row.find('span', class_='zt')
            location = ""
            if location_span:
                # 获取完整的位置文本
                location_text = location_span.get_text(strip=True)
                # 移除位置图标前缀
                # 使用正则表达式更精确地提取地点信息
                location_match = re.search(r'(?:\uf041)?(.+)', location_text)
                if location_match:
                    location = location_match.group(1).strip()
            
            if course_name or time_text or location:
                courses.append({
                    "name": course_name,
                    "time": time_text,
                    "location": location
                })
        
        if courses:
            print("成功从页面提取到课程信息!")
            return courses
        else:
            print("未能从页面提取课程信息")
            return []
        
    except Exception as e:
        print(f"获取课表时出错: {e}")
        return []

def display_courses(courses):
    """美观地显示课程信息"""
    if not courses:
        print("\n未找到今日课程信息")
        return
    
    print("\n===== 今日课表 =====")
    for i, course in enumerate(courses, 1):
        print(f"\n【第{i}节课】")
        if 'name' in course and course['name']:
            print(f"课程: {course['name']}")
        if 'time' in course and course['time']:
            # 确保时间格式美观
            time_str = course['time']
            # 清理掉多余空格和换行
            time_str = re.sub(r'\s+', ' ', time_str)
            print(f"时间: {time_str}")
        if 'location' in course and course['location']:
            print(f"地点: {course['location']}")
    
    print("\n====================")

def get_weather_forecast():
    """获取和风天气24小时天气预报数据"""
    print("\n正在获取天气预报...")
    
    try:
        params = {
            "location": LOCATION,
            "key": WEATHER_API_KEY,
        }
        
        response = requests.get(WEATHER_API_URL, params=params)
        
        if response.status_code == 200:
            weather_data = response.json()
            if weather_data.get("code") == "200":
                print("✅ 成功获取天气预报")
                return weather_data.get("hourly", [])
            else:
                print(f"❌ 获取天气预报失败: {weather_data.get('code')}")
                return []
        else:
            print(f"❌ 天气API请求失败，状态码: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ 获取天气预报出错: {e}")
        return []

def generate_course_html(courses, weather_data=None):
    """生成简单紧凑的表格样式HTML课表，包含天气预报信息"""
    # 获取当前日期
    now = datetime.datetime.now()
    weekday = ["一", "二", "三", "四", "五", "六", "日"][now.weekday()]
    date_str = now.strftime("%Y年%m月%d日")
    
    # 提取天气数据
    current_weather = {}
    if weather_data and len(weather_data) > 0:
        # 获取第一条记录作为当前天气
        current_weather = weather_data[0]
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>今日课表</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif;
            }}
            body {{
                padding: 0;
                margin: 0;
                color: #333;
                font-size: 14px;
            }}
            .header {{
                background: #4a89dc;
                color: white;
                padding: 10px;
                text-align: center;
            }}
            .header h1 {{
                font-size: 16px;
                font-weight: normal;
                margin: 0;
            }}
            .date {{
                font-size: 12px;
                margin-top: 4px;
            }}
            .weather {{
                background: #f5f7fa;
                padding: 8px;
                display: flex;
                justify-content: space-around;
                border-bottom: 1px solid #e6e6e6;
            }}
            .weather-item {{
                text-align: center;
                font-size: 12px;
            }}
            .weather-item .value {{
                font-size: 14px;
                font-weight: 500;
                margin-top: 2px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 6px 8px;
                text-align: left;
                border-bottom: 1px solid #e6e6e6;
                font-size: 13px;
            }}
            th {{
                background-color: #f2f2f2;
                font-weight: normal;
                color: #666;
                text-align: center;
            }}
            td {{
                text-align: center;
            }}
            .no-course {{
                text-align: center;
                padding: 15px;
                color: #666;
            }}
            .footer {{
                padding: 8px;
                text-align: center;
                font-size: 11px;
                color: #999;
                background: #f8f8f8;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .course-row:hover {{
                background-color: #f0f7ff;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>今日课表</h1>
            <div class="date">星期{weekday}·{date_str}</div>
        </div>
    """
    
    # 添加天气预报部分
    if current_weather:
        html += f"""
        <div class="weather">
            <div class="weather-item">
                <div>天气</div>
                <div class="value">{current_weather.get('text', '未知')}</div>
            </div>
            <div class="weather-item">
                <div>温度</div>
                <div class="value">{current_weather.get('temp', '未知')}°C</div>
            </div>
            <div class="weather-item">
                <div>湿度</div>
                <div class="value">{current_weather.get('humidity', '未知')}%</div>
            </div>
            <div class="weather-item">
                <div>风向</div>
                <div class="value">{current_weather.get('windDir', '未知')}</div>
            </div>
        </div>
        """
    
    if not courses:
        html += """
        <div class="no-course">
            <p>今日没有课程安排</p>
        </div>
        """
    else:
        html += """
        <table>
            <thead>
                <tr>
                    <th>序号</th>
                    <th>课程</th>
                    <th>时间</th>
                    <th>地点</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for i, course in enumerate(courses, 1):
            name = course.get('name', '未知课程')
            time = course.get('time', '时间未知')
            location = course.get('location', '地点未知')
            
            html += f"""
                <tr class="course-row">
                    <td>{i}</td>
                    <td>{name}</td>
                    <td>{time}</td>
                    <td>{location}</td>
                </tr>
            """
        
        html += """
            </tbody>
        </table>
        """
    
    # 添加未来天气预报
    if weather_data and len(weather_data) > 1:
        forecast_items = weather_data[1:6]  # 只显示接下来5小时的天气预报
        
        html += """
        <div style="padding: 10px;">
            <div style="margin-bottom: 6px; color: #666; font-size: 13px; border-bottom: 1px solid #eee; padding-bottom: 4px;">近期天气预报</div>
            <div style="display: flex; overflow-x: auto; padding-bottom: 5px;">
        """
        
        for item in forecast_items:
            # 转换时间格式 2021-02-16T15:00+08:00 -> 15:00
            time_str = "未知"
            try:
                time_match = re.search(r'T(\d{2}:\d{2})\+', item.get('fxTime', ''))
                if time_match:
                    time_str = time_match.group(1)
            except:
                pass
            
            html += f"""
                <div style="min-width: 60px; text-align: center; margin-right: 10px;">
                    <div style="font-size: 12px; color: #666;">{time_str}</div>
                    <div style="margin: 4px 0; font-weight: 500;">{item.get('temp', '未知')}°C</div>
                    <div style="font-size: 11px;">{item.get('text', '未知')}</div>
                </div>
            """
        
        html += """
            </div>
        </div>
        """
    
    html += """
        <div class="footer">
            课表自动推送系统·每日更新
        </div>
    </body>
    </html>
    """
    
    return html

def push_to_wxpusher(courses, weather_data=None):
    """推送课表和天气到微信"""
    if not courses and not weather_data:
        content = generate_course_html([], [])
        summary = "今日没有课程安排"
    else:
        content = generate_course_html(courses, weather_data)
        # 生成摘要，最多显示前三门课
        course_summary = []
        for i, course in enumerate(courses[:3], 1):
            if i > 3:
                break
            course_summary.append(course.get('name', '未知课程'))
        
        if len(courses) > 3:
            summary = f"今日课程: {', '.join(course_summary)}等{len(courses)}门课"
        else:
            summary = f"今日课程: {', '.join(course_summary)}"
        
        # 如果有天气，添加天气信息
        if weather_data and len(weather_data) > 0:
            current_weather = weather_data[0]
            temp = current_weather.get('temp', '')
            text = current_weather.get('text', '')
            if temp and text:
                weather_summary = f" 天气:{text} {temp}°C"
                # 确保摘要不超过20个字符
                if len(summary) + len(weather_summary) <= 20:
                    summary += weather_summary
        
        # 确保摘要不超过20个字符
        if len(summary) > 20:
            summary = summary[:17] + "..."
    
    # 构造请求数据
    data = {
        "appToken": APP_TOKEN,
        "content": content,
        "summary": summary,
        "contentType": 2,  # 2表示HTML
        "topicIds": [TOPIC_ID],
        "verifyPayType": 0  # 不验证付费
    }
    
    try:
        # 发送请求
        print("\n正在推送课表到微信...")
        response = requests.post(WXPUSHER_API_URL, json=data)
        
        # 处理响应
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 1000:
                print("✅ 课表推送成功!")
                return True
            else:
                print(f"❌ 课表推送失败: {result.get('msg')}")
                return False
        else:
            print(f"❌ 课表推送请求失败，状态码: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ 课表推送出错: {e}")
        return False

if __name__ == "__main__":
    session = login()
    if session:
        courses = get_homepage_courses(session)
        display_courses(courses)
        
        # 获取天气数据
        weather_data = get_weather_forecast()
        
        # 推送课表和天气到微信
        push_to_wxpusher(courses, weather_data) 
