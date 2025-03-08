# a1
2025Douban Movie Recommender Analyzer Python 爬虫项目，用于自动化采集豆瓣电影推荐数据并进行结构化分析，爬取20年代以来的电影数据，支持动态分页采集与数据异常处理。本指南详细阐述技术实现流程与关键模块设计。
核心功能
动态分页采集：通过 API 参数迭代获取全量数据
反爬策略：请求头模拟、Cookies 维护、随机延迟
数据清洗：缺失值填充、嵌套 JSON 解析
持久化存储：JSON 结构化存储与 Pandas DataFrame 转换
技术栈
请求处理：requests库实现 API 调用
数据解析：json模块处理结构化响应
异常管理：try-except容错机制
数据分析：pandas实现数据标准化
反爬策略：随机化请求间隔与 Cookies 维护
实现步骤详解
一、网页类型判定（静态 / 动态）
API 特征识别
目标 URL 为https://m.douban.com/rexxar/api/v2/movie/recommend，使用.json数据接口
通过 Chrome DevTools 的 Network 面板验证 XHR 请求，确认数据通过 AJAX 动态加载
网页数据转换成python，我用在线工具：https://www.lddgo.net/convert/curl-to-code
修改start参数观察响应内容变化（如start=20返回第二页数据）
内容验证方法
直接访问页面 URL 返回空白内容，需特定参数触发数据加载
响应头包含Content-Type: application/json，确认数据为结构化格式
二、数据解析流程
JSON 结构化处理
python
Copy
data = response.json()
items = data.get('items', [])

嵌套字段提取
采用链式.get()方法处理多级字典结构，避免KeyError异常：
python
Copy
comment = item.get('comment', {}).get('comment', '无评论')
rating = item.get('rating', {}).get('value', '无评分')

数据标准化转换
使用pd.json_normalize将嵌套 JSON 转换为平面数据结构：
python
Copy
df = pd.json_normalize(raw_json['items'], max_level=2)

三、Cookies 自动化管理
会话维持机制
创建持久化会话对象降低连接开销：
python
Copy
self.session = requests.Session()
self.session.cookies.update(self.cookies)

动态刷新策略
监控403 Forbidden状态码触发 Cookies 更新
集成 Selenium 实现自动化登录获取新 Cookies（需单独配置）
请求头伪装
完整模拟浏览器 Headers 参数，重点维护：
python
Copy
'user-agent': 'Mozilla/5.0...',
'referer': 'https://movie.douban.com/explore'

四、分页采集策略
参数动态生成
每页 20 条数据，通过start参数实现分页：
python
Copy
params = {
    'refresh': '0',
    'start': page * 20,
    'count': 20,
    'ck': '77v1'
}

终止条件判定
最大页数限制（max_pages=30）
响应状态码非 200 或返回空items列表时终止采集
反爬延迟机制
随机化请求间隔模拟人工操作：
python
Copy
time.sleep(random.uniform(1, 3))

注意事项
法律合规
遵守豆瓣 Robots 协议 (/robots.txt)
单 IP 请求频率控制在 30 次 / 分钟以下
数据存储优化
采用增量存储避免重复采集

python
Copy
with open('data.json', 'a', encoding='utf-8') as f:
    json.dump(new_items, f, ensure_ascii=False)

异常监控
网络异常重试机制（retrying库）
数据完整性校验（记录已采集 ID 列表）
示例代码段
python
Copy
# 分页采集核心逻辑
max_pages = 30
page = 0  
all_data = []
while page < max_pages:
    params = {'start': page * 20, 'count': 20}
    response = self.session.get(self.url, params=params)
    
    if response.status_code != 200:
        break
        
    data = response.json()
    if not data.get('items'):
        break
        
    all_data.extend(data['items'])
    page += 1
本方案通过 API 逆向分析实现高效数据采集，结合多维度反爬策略保障系统稳定性。建议部署至云服务器并配置定时任务实现长期运行。
