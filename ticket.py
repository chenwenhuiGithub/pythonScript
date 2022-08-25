# -*- coding: utf-8 -*-
import requests
import json
import re
import prettytable as pt


class ticket:
    def __init__(self, from_station_name, to_station_name, train_date, purpose_codes='ADULT'):
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'}
        self.session = requests.Session()
        self.from_station_name = from_station_name
        self.to_station_name = to_station_name
        self.train_date = train_date
        self.purpose_codes = purpose_codes
        self.from_station_code = ''
        self.to_station_code = ''
        self.query_url = ''
        self.login_url = ''
        self.jsessionid = ''

    def get_station_code(self):
        url = 'https://www.12306.cn/index/script/core/common/station_name_v10178.js'
        resp = self.session.get(url, headers=self.headers)

        from_station_index = resp.text.index(self.from_station_name) + len(self.from_station_name)
        while (resp.text[from_station_index] != '|'):
            from_station_index = resp.text.index(self.from_station_name, from_station_index + len(self.from_station_name)) + len(self.from_station_name)

        to_station_index = resp.text.index(self.to_station_name) + len(self.to_station_name)
        while (resp.text[to_station_index] != '|'):
            to_station_index = resp.text.index(self.to_station_name, to_station_index + len(self.to_station_name)) + len(self.to_station_name)

        self.from_station_code = resp.text[from_station_index+1:from_station_index+4]
        self.to_station_code = resp.text[to_station_index+1:to_station_index+4]
        print('from_station:', self.from_station_name + ' - ' + self.from_station_code) # 杭州 - HZH
        print('to_station:', self.to_station_name + ' - ' + self.to_station_code)       # 信阳 - XUN

    def get_index_login_conf(self):
        url = 'https://www.12306.cn/index/otn/login/conf'
        headers = {
            'ContentType':'application/json;charset=UTF-8',
            'User-Agent':self.headers['User-Agent']
        }
        resp = self.session.post(url, headers=headers)
        resp.encoding = 'utf-8'
        dic = json.loads(resp.text)

        self.query_url = dic['data']['queryUrl']
        self.jsessionid = re.search(r'(.*)JSESSIONID=(.*?);', resp.headers.get('Set-Cookie')).group(2)
        print('query_url:', dic['data']['queryUrl']) # leftTicket/query
        print('jsessionid:', self.jsessionid)        # 68F423A7858C3C22FA617AAA5D4EAA7E

    def query_left_ticket(self):
        url = 'https://kyfw.12306.cn/otn/' + self.query_url
        params = {
            'leftTicketDTO.train_date':self.train_date,
            'leftTicketDTO.from_station':self.from_station_code,
            'leftTicketDTO.to_station':self.to_station_code,
            'purpose_codes':self.purpose_codes
        }
        headers = {
            'ContentType':'application/json;charset=UTF-8',
            'User-Agent':self.headers['User-Agent'],
            'Cookie':'JSESSIONID=' + self.jsessionid
        }
        resp = self.session.get(url, params=params, headers=headers)
        resp.encoding = 'utf-8'
        dic = json.loads(resp.text)

        tb = pt.PrettyTable()
        tb.field_names = ["车次", "出发/到达站", "出发/到达时间", "历时", "商务座", "一等座", "二等座", "高级软卧", "软卧", "动卧", "硬卧", "软座", "硬座", "无座"]

        map = dic['data']['map']
        result_list = dic['data']['result']
        for result_item in result_list:
            items = result_item.split('|')
            tb.add_row([
                items[3], # 车次
                map[items[6]] + ' - ' + map[items[7]], # 出发/到达站
                items[8] + ' - ' + items[9], # 出发/到达时刻
                items[10], # 历时
                items[32] or '-', # 商务座
                items[31] or '-', # 一等座
                items[30] or '-', # 二等座
                items[21] or '-', # 高级软卧
                items[23] or '-', # 软卧
                items[27] or '-', # 动卧
                items[28] or '-', # 硬卧
                items[24] or '-', # 软座
                items[29] or '-', # 硬座
                items[26] or '-'  # 无座
            ])
        print(tb)


if __name__ == '__main__':
    ticket_object = ticket('杭州', '信阳', '2022-09-01')
    ticket_object.get_station_code()
    ticket_object.get_index_login_conf()
    ticket_object.query_left_ticket()
