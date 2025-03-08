import json
import pandas as pd
import requests
import time
import random
from bs4 import BeautifulSoup

class Mind:
    def getdata(self):
        self.url='https://m.douban.com/rexxar/api/v2/movie/recommend?'
        self.cookies = {
            'bid': 'pWlARMDCrX0',
            'll': '"118204"',
            '_vwo_uuid_v2': 'D78943541603B8793DA8D893E66003022|44e33beebb5fe2164aa1e12aa75939be',
            'Hm_lvt_6d4a8cfea88fa457c3127e14fb5fabc2': '1739025309',
            '_ga': 'GA1.2.555498124.1739025310',
            '_ga_Y4GN1R87RG': 'GS1.1.1739025309.1.0.1739025312.0.0.0',
            'dbcl2': '"182143236:57u/RF5c+kg"',
            'push_doumail_num': '0',
            'push_noty_num': '0',
            '__utmv': '30149280.18214',
            'ck': '77v1',
            'frodotk_db': '"e7dc9f5acb22a355b795de106167e9ff"',
            '__utmc': '30149280',
            '__utmz': '30149280.1741349218.13.5.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/',
            'frodotk': '"7019f4c41e6612ca504dde4c5b32385e"',
            'talionusr': '"eyJpZCI6ICIxODIxNDMyMzYiLCAibmFtZSI6ICJZaEVhT2hBbyJ9"',
            'ap_v': '0,6.0',
            '__utma': '30149280.68469296.1734620096.1741349218.1741360620.14',
            '__utmb': '30149280.0.10.1741360620',
        }

        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'origin': 'https://movie.douban.com',
            'priority': 'u=1, i',
            'referer': 'https://movie.douban.com/explore',
            'sec-ch-ua': '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
            # Requests sorts cookies= alphabetically
            # 'cookie': 'bid=pWlARMDCrX0; ll="118204"; _vwo_uuid_v2=D78943541603B8793DA8D893E66003022|44e33beebb5fe2164aa1e12aa75939be; Hm_lvt_6d4a8cfea88fa457c3127e14fb5fabc2=1739025309; _ga=GA1.2.555498124.1739025310; _ga_Y4GN1R87RG=GS1.1.1739025309.1.0.1739025312.0.0.0; dbcl2="182143236:57u/RF5c+kg"; push_doumail_num=0; push_noty_num=0; __utmv=30149280.18214; ck=77v1; frodotk_db="e7dc9f5acb22a355b795de106167e9ff"; __utmc=30149280; __utmz=30149280.1741349218.13.5.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/; frodotk="7019f4c41e6612ca504dde4c5b32385e"; talionusr="eyJpZCI6ICIxODIxNDMyMzYiLCAibmFtZSI6ICJZaEVhT2hBbyJ9"; ap_v=0,6.0; __utma=30149280.68469296.1734620096.1741349218.1741360620.14; __utmb=30149280.0.10.1741360620',
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
