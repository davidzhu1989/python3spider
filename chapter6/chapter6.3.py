#!/usr/bin/env python
# @Time : 2019/3/19 20:38
__author__ = 'Boaz'

from pyquery import PyQuery as pq
from urllib.parse import urlencode
from pymongo import MongoClient
import requests
base_url = 'https://m.weibo.cn/api/container/getIndex?'

headers = {
    'Host': 'm.weibo.cn',
    'Referer': 'https://m.weibo.cn/u/2830678474',
    'User-Agent': 'Mozilla/5.0(Macintosh; Intel Mac OS X 10_12_3)'
                  'AppleWebKit/537.36 (KHTML, like Gecko)'
                  'Chrome/58.0.3029.110 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}
client = MongoClient(host='localhost', port=27017)
db = client['weibo']
collection = db['weibo']
max_page = 10


def get_page(page):
    params = {
        'type': 'uid',
        'value': '2830678474',
        'containerid': '1076032830678474',
        'page': page
    }
    url = base_url + urlencode(params)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json(), page
    except requests.ConnectionError as e:
        print('Error', e.args)


# def parse_page(json):
#     if json:
#         items = json.get('data').get('cards')
#         for index, item in enumerate(items):
#             item = item.get('mblog',{})
#             weibo = {}
#             weibo['id'] = item.get('id')
#             weibo['text'] = pq(item.get('text')).text()
#             weibo['attitudes'] = item.get('attitudes_count')
#             weibo['comments'] = item.get('comments_count')
#             weibo['reposts'] = item.get('reposts_count')
#             print('-----------------')
#             print('已经读取了一条')
#             yield weibo

def parse_page(json, page: int):
    if json:
        items = json.get('data').get('cards')
        for index, item in enumerate(items):
            if page == 1 and index == 1:
                continue
            else:
                item = item.get('mblog', {})
                weibo = {}
                weibo['id'] = item.get('id')
                weibo['text'] = pq(item.get('text')).text()
                weibo['attitudes'] = item.get('attitudes_count')
                weibo['comments'] = item.get('comments_count')
                weibo['reposts'] = item.get('reposts_count')
                yield weibo


def save_to_mongo(result):
    if collection.insert(result):
        print('saved to Local mongo')


if __name__ == '__main__':
    for page in range(1, max_page + 1):
        json = get_page(page)
        results = parse_page(*json)
        for result in results:
            print(result)
            save_to_mongo(result)
