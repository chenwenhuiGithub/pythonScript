# -*- coding: utf-8 -*-
import requests
import json
import re
import time
import qrcode
import os
import base64
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
        self.uuid = ''
        # TODO: get rail_deviceid and rail_expiration
        self.rail_deviceid = 'ri4SGw5nqap-u7g3dyz6X3EtPJAdqaGeNm9-n94W-stEgktjUeHm1kcMPm6HIJMptC4sK7jZke5RIgC6U0cBWJtdx8EhwAnSzaB55RR65TwV_HeoGo5H_oLPMukVmPLswj-wxh73iEIGEYokiYpI7ISQHzgv6EIK'
        self.rail_expiration = '1661601931084'
        self.qrcode_filename = 'qrcode.png'
        self.newapptk = ''
        self.username = ''

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
        resp = self.session.post(url, headers=self.headers)
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

    def gen_qrcode(self):
        url = 'https://kyfw.12306.cn/passport/web/create-qr64'
        data = {
            'appid':'otn'
        }
        resp = self.session.post(url, data=data, headers=self.headers)
        resp.encoding = 'utf-8'
        dic = json.loads(resp.text)

        self.uuid = dic['uuid']
        print('uuid:', self.uuid)

        image_bytes = base64.b64decode(dic['image'])
        with open(self.qrcode_filename, 'wb') as f:
            f.write(image_bytes)
        os.startfile(self.qrcode_filename)

        #qr = qrcode.QRCode(error_correction=qrcode.ERROR_CORRECT_L, box_size=5)
        #qr.add_data(image_bytes)
        # qr.print_ascii(invert=False)
        #qr.make_image().show() # pip3 install image
        print('get qrcode success, please scan')

    def check_qrcode(self):
        url = 'https://kyfw.12306.cn/passport/web/checkqr'
        while True:
            params = {
                'RAIL_DEVICEID':self.rail_deviceid,
                'RAIL_EXPIRATION':self.rail_expiration,
                'uuid':self.uuid,
                'appid':'otn'
            }
            resp = self.session.post(url, params=params, headers=self.headers)
            resp.encoding = 'utf-8'
            dic = json.loads(resp.text)

            result_code = dic['result_code']
            if result_code == '0': # not scan
                print('qrcode not scan')
            elif result_code == 1: # scan success
                print('qrcode scan success, please confirm on phone')
            elif result_code == 2: # login success
                print('qrcode login success')
                return
            elif result_code == 3: # qrcode invalid
                print('qrcode scan timeout')
                return
            else:
                print('qrcode login failed, result code:%s', result_code)
                return
            time.sleep(1)

    def auth_uamtk(self):
        url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
        data = {
            'appid':'otn'
        }
        resp = self.session.post(url, data=data, headers=self.headers)
        resp.encoding = 'utf-8'
        dic = json.loads(resp.text)

        self.newapptk = dic['newapptk']
        print('newapptk:', self.newapptk)

    def auth_uamauthclient(self):
        url = 'https://kyfw.12306.cn/otn/uamauthclient'
        data = {
            'tk':self.newapptk
        }
        resp = self.session.post(url, data=data, headers=self.headers)
        resp.encoding = 'utf-8'
        dic = json.loads(resp.text)

        self.username = dic['username']
        print('username:', self.username)

    def initMy12306Api(self):
        url = 'https://kyfw.12306.cn/otn/index/initMy12306Api'
        resp = self.session.post(url, headers=self.headers)
        resp.encoding = 'utf-8'
        dic = json.loads(resp.text)
        print('login success ' + self.username + ' ' + dic['user_regard'])

    def query_passengers(self):
        url = 'https://kyfw.12306.cn/otn/passengers/query'
        data = {
            'pageIndex':'1',
            'pageSize':'10'
        }
        resp = self.session.post(url, data=data, headers=self.headers)
        resp.encoding = 'utf-8'
        dic = json.loads(resp.text)

        tb = pt.PrettyTable()
        tb.field_names = ['姓名', '性别', '生日', '证件号码', '手机/电话', '旅客类型']

        passenger_list = dic['data']['datas']
        for passenger_item in passenger_list:
            tb.add_row([
                passenger_item['passenger_name'],
                passenger_item['sex_name'],
                passenger_item['born_date'],
                passenger_item['passenger_id_no'],
                passenger_item['mobile_no'],
                passenger_item['passenger_type_name']
            ])
        print(tb)

if __name__ == '__main__':
    ticket_object = ticket('杭州', '信阳', '2022-09-01')
    ticket_object.get_station_code()
    ticket_object.get_index_login_conf()
    ticket_object.query_left_ticket()
    ticket_object.gen_qrcode()
    ticket_object.check_qrcode()
    ticket_object.auth_uamtk()
    ticket_object.auth_uamauthclient()
    ticket_object.initMy12306Api()
    ticket_object.query_passengers()
