# -*- coding: utf-8 -*-
import requests
import prettytable as pt


class ticket:
    def __init__(self, proxies=None):
        self.headers = { 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36' }    
        self.proxies = proxies
        self.session = requests.Session()

    
if __name__ == '__main__':
    ticket_object = ticket()

    tb = pt.PrettyTable()
    tb.field_names = ["车次", "出发/到达站", "出发/到达时间", "历时", "商务座", "一等座", "二等座", "高级软卧", "软卧", "动卧", "硬卧", "软座", "硬座", "无座"]
    tb.add_row(["K468", "信阳 - 杭州", "00:15 - 10:57", "10h:42m", "-", "-", "-", "-", "无", "-", 5, "-", 124, "无"])
    tb.add_row(["G1793", "信阳东 - 杭州东", "09:00 - 14:31", "05h:31m", 20, "有", "有", "-", "-", "-", "-", "-", "-", "-"])
    tb.add_row(["K752", "信阳 - 杭州南", "13:30 - 02:35", "13h:05m", "-", "-", "-", "-", 34, "-", 2, "-", 56, "无"])
    tb.set_style(pt.SINGLE_BORDER)
    print(tb)
