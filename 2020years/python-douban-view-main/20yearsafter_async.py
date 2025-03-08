import json
import pandas as pd
import requests
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
import pickle
import time



class Mind:
    def refresh_cookie():          #cookie自动化 低频访问
        driver = webdriver.Chrome()
        try:
            driver.get("https://www.douban.com/login")
            # 执行登录动作（需提前注入账号密码）
            driver.find_element("name", "form_email").send_keys("your_account")
            driver.find_element("name", "form_password").send_keys("your_pwd")

            # 验证码处理分支
            if "captcha_image" in driver.page_source:
                captcha = input("手动输入验证码：")
                driver.find_element("id", "captcha_field").send_keys(captcha)

            driver.find_element("xpath", "//input[@class='btn-submit']").click()
            time.sleep(5)

            # 持久化新Cookie
            with open("douban_cookies.pkl", "wb") as f:
                pickle.dump(driver.get_cookies(), f)

        finally:
            driver.quit()

    def getdata(self):
        self.url='https://m.douban.com/rexxar/api/v2/movie/recommend?'
        self.headers = {                #修改为自己的user-agent
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'origin': 'https://movie.douban.com',
            'priority': 'u=1, i',
            'referer': 'https://movie.douban.com/explore',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
              }

        max_pages = 10
        page = 0  # 初始化页码
        all_data=[]
        while page < max_pages:
            params = {
                'refresh': '0',
                'start': page * 20,  # 动态计算起始位置
                'count': 20,
                'selected_categories': '{}',
                'uncollect': 'false',
                'tags': '',
                'ck': '77v1',
            }

            response = requests.get('https://m.douban.com/rexxar/api/v2/movie/recommend',
                                    params=params,
                                    cookies=self.cookies,
                                    headers=self.headers)

            if response.status_code != 200:
                break

            data = response.json()
            if not data.get('items'):
                break
            all_data.extend(data['items'])

            time.sleep(random.uniform(1, 3))  # 反爬延迟
            page += 1  # 页码递增
        return all_data

    def write_data(self):
        all_times = self.getdata()
        if all_times: # 提取JSON数据
            with open('moviedata.txt', 'w', encoding='utf-8') as f:
                json.dump({'items': all_times}, f, ensure_ascii=False)  #将请求存储在csv json正确格式

    def path_find(self):  #将1.txt的元素定位用法
        try:
            with open('moviedata.txt','r',encoding='utf-8')as f:
                data= json.load(f)  #loads方法格式化f传进data
            df = self.process_missing_data(data)
            print("\n处理后的结构化数据：")
            print(df.head())

        except Exception as e:
            for item in data.get('items'):
                print(f"电影名字：{item.get('title','无标题')}",
                      f"年份：{item.get('year','无年份')}",
                      f"评分：{item.get('rating', {}).get('value','无评分')}",
                      f"精选短评：{item.get('comment',{}).get('comment','无评分')}" #无透露真实用户id及用户名

                      )


        except IOError as e:
            print("没获得到")
        # print()

    def process_missing_data(self, raw_json):  # 注意添加self参数
        if not raw_json.get('items'):
            raise ValueError("JSON数据缺失'items'字段")

        # 安全转换DataFrame
        df = pd.json_normalize(raw_json['items'], max_level=2)

        # 年份字段：中位数填充缺失值
        if 'year' in df.columns:
            median_year = df['year'].median() if not df['year'].isnull().all() else 0
            df['year'] = df['year'].fillna(median_year).astype(int)
        else:
            df['year'] = 0  # 字段缺失时初始化

if __name__ == '__main__':
    obj = Mind()
    obj.write_data()  # 触发分页数据采集
    obj.path_find()   # 处理数据管道
