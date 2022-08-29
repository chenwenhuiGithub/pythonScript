# -*- coding: utf-8 -*-
from email import header
from http import cookies
import requests
import json
import re
import time
import os
import base64
import prettytable as pt


class ticket:
    def __init__(self, from_station_name, to_station_name, train_date, purpose_codes='ADULT'):
        self.session = requests.Session()
        self.session.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'}
        self.cookies_BIGipServerotn_kyfw_12306_cn = ''
        self.cookies_BIGipServerotn_www_12306_cn = ''
        self.cookies_BIGipServerpool_index_www_12306_cn = ''
        self.cookies_route_www_12306_cn = ''
        self.cookies_JSESSIONID_www_12306_cn_index_otn = ''
        self.cookie_BIGipServerpassport_kyfw_12306_cn = ''
        self.cookie_passport_session_kyfw_12306_cn_passport = ''
        self.cookies_route_kyfw_12306_cn = ''
        self.cookies_JSESSIONID_kyfw_12306_cn_otn = ''

        self.from_station_name = from_station_name
        self.to_station_name = to_station_name
        self.train_date = train_date
        self.purpose_codes = purpose_codes
        self.from_station_code = ''
        self.to_station_code = ''
        self.rail_deviceid = ''
        self.rail_expiration = ''
        self.queryUrl = ''
        self.fo = ''
        self.uuid = ''
        self.qrcode_filename = 'qrcode.png'

        self.login_url = ''
        self.jsessionid = ''
        self.newapptk = ''
        self.username = ''

    def get_otn_httpzf_getjs(self):
        url = 'https://kyfw.12306.cn/otn/HttpZF/GetJS'
        resp = self.session.get(url)

        print('\nget_otn_httpzf_getjs')
        print(resp.request.headers)
        print(resp.cookies)
        print(self.session.cookies)

        self.cookies_BIGipServerotn_kyfw_12306_cn = self.session.cookies.get('BIGipServerotn', domain='kyfw.12306.cn')
        print('cookies_BIGipServerotn_kyfw_12306_cn:', self.cookies_BIGipServerotn_kyfw_12306_cn)

    def get_otn_httpzf_logdevice(self):
        url = 'https://kyfw.12306.cn/otn/HttpZF/logdevice'
        resp = self.session.get(url)

        print('\nget_otn_httpzf_logdevice')
        print(resp.request.headers)
        print(resp.cookies)
        print(self.session.cookies)

        dic = json.loads(resp.text[18:-2]) # remove prefix 'callbackFunction'
        self.rail_deviceid = dic['dfp']
        self.rail_expiration = dic['exp']
        print('rail_deviceid:', self.rail_deviceid)
        print('rail_expiration:', self.rail_expiration)

    def post_index_otn_login_conf(self):
        url = 'https://www.12306.cn/index/otn/login/conf'
        resp = self.session.post(url)

        print('\npost_index_otn_login_conf')
        print(resp.request.headers)
        print(resp.cookies)
        print(self.session.cookies)

        self.cookies_BIGipServerotn_www_12306_cn = self.session.cookies.get('BIGipServerotn', domain='www.12306.cn')
        self.cookies_BIGipServerpool_index_www_12306_cn = self.session.cookies.get('BIGipServerpool_index', domain='www.12306.cn')
        self.cookies_route_www_12306_cn = self.session.cookies.get('route', domain='www.12306.cn')
        self.cookies_JSESSIONID_www_12306_cn_index_otn = self.session.cookies.get('JSESSIONID', domain='www.12306.cn')
        print('cookies_BIGipServerotn_www_12306_cn:', self.cookies_BIGipServerotn_www_12306_cn)
        print('cookies_BIGipServerpool_index_www_12306_cn:', self.cookies_BIGipServerpool_index_www_12306_cn)
        print('cookies_route_www_12306_cn:', self.cookies_route_www_12306_cn)
        print('cookies_JSESSIONID_www_12306_cn_index_otn:', self.cookies_JSESSIONID_www_12306_cn_index_otn)

        dic = json.loads(resp.text)
        self.queryUrl = dic['data']['queryUrl']
        print('queryUrl:', self.queryUrl)

    def get_station_code(self):
        url = 'https://www.12306.cn/index/script/core/common/station_name_v10178.js'
        resp = self.session.get(url)

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

    def query_left_ticket(self):
        url = 'https://kyfw.12306.cn/otn/' + self.queryUrl
        params = {
            'leftTicketDTO.train_date':self.train_date,
            'leftTicketDTO.from_station':self.from_station_code,
            'leftTicketDTO.to_station':self.to_station_code,
            'purpose_codes':self.purpose_codes
        }
        cookies = {
            # JSESSIONID cookie Path=/index/otn, so need add it explicitly
            'JSESSIONID':self.session.cookies.get('JSESSIONID') # 1EE31D3AF6EF9BC59E242314F8C32FC0
        }
        resp = self.session.get(url, params=params, cookies=cookies)

        print('\nquery_left_ticket')
        print(resp.request.headers)
        print(resp.headers)
        print(resp.cookies)
        print(self.session.cookies)

        tb = pt.PrettyTable()
        tb.field_names = ["车次", "出发/到达站", "出发/到达时间", "历时", "商务座", "一等座", "二等座", "高级软卧", "软卧", "动卧", "硬卧", "软座", "硬座", "无座"]

        dic = json.loads(resp.text)
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

    def post_passport_web_auth_uamtk_static(self):
        url = 'https://kyfw.12306.cn/passport/web/auth/uamtk-static'
        data = {
            'appid':'otn'
        }
        resp = self.session.post(url, data=data)

        print('\npost_passport_web_auth_uamtk_static')
        print(resp.request.headers)
        print(resp.cookies)
        print(self.session.cookies)

        self.cookie_BIGipServerpassport_kyfw_12306_cn = self.session.cookies.get('BIGipServerpassport', domain='kyfw.12306.cn')
        self.cookie_passport_session_kyfw_12306_cn_passport = self.session.cookies.get('_passport_session', domain='kyfw.12306.cn')
        print('cookie_BIGipServerpassport_kyfw_12306_cn:', self.cookie_BIGipServerpassport_kyfw_12306_cn)
        print('cookie_passport_session_kyfw_12306_cn_passport:', self.cookie_passport_session_kyfw_12306_cn_passport)

    def post_otn_login_conf(self):
        url = 'https://kyfw.12306.cn/otn/login/conf'
        cookies = {
            'guidesStatus':'off',
            'highContrastMode':'defaltMode',
            'cursorStatus':'off',
            'RAIL_EXPIRATION':self.rail_expiration,
            'RAIL_DEVICEID':self.rail_deviceid
        }
        resp = self.session.post(url, cookies=cookies)

        print('\npost_otn_login_conf')
        print(resp.request.headers)
        print(resp.cookies)
        print(self.session.cookies)

        self.cookies_route_kyfw_12306_cn = self.session.cookies.get('route', domain='kyfw.12306.cn')
        self.cookies_JSESSIONID_kyfw_12306_cn_otn = self.session.cookies.get('JSESSIONID', domain='kyfw.12306.cn')
        print('cookies_route_kyfw_12306_cn:', self.cookies_route_kyfw_12306_cn)
        print('cookies_JSESSIONID_kyfw_12306_cn_otn:', self.cookies_JSESSIONID_kyfw_12306_cn_otn)

        dic = json.loads(resp.text)
        self.queryUrl = dic['data']['queryUrl']
        print('queryUrl:', self.queryUrl)

    def post_otn_logsdk_getinfo(self):
        url = 'https://kyfw.12306.cn/otn/logsdk/getInfo'
        json_param = { # TODO: get secretInfo
            'secretInfo':'2rF1n09InsQIqpkpWGc8fT4/rVgXysmFOpgvgc9V5kfGexUGYAHA/Prnh5mhE6XhMQvPLsCitnocobDrqRKrcHzngnYllRUEog9jrngKQxny3a4P0ed1oWelW84QNCMF1+FVAMUTPJM6b3MeH64z/0O0UWpWM79Bbeeo3CnBvENp5KlVymYsMT642tlts5ldjhQNlmEaz8ZL0dCSimmhNiQR8YYbPzOtgCYjv0BJufbJrpW8YRCW39vlc2OAPeFz7mpkMfQd5N/krC6oSlzX4M3lFWjGmW4TvQ/Yb8qRQFOYAjl4a4KPALvUhy1yLldYUSs/jSizbCN6yWwKWWckfryAfOlMLRiopQoYocaldwuDx+99ZYts4mznwpybefZ14dJvykikGekAW5fitAhHYYN7zNuj7aRsf4DTo06xLF9rYnfLkS82TcQau0ZLQ8S20NmDr/f2YmjuSHGlVnH4o2omObI41REyVSh9EOFGi8dXJSdgHBn0R2Co09VkmfmRQg3K/nb0wJZCnw/cETqDZoGNU8PPh9K3cviGfTyFvLipw+2JX00+KpgtqxNmRib4KOQ4237ApJ4TdOJzWrYUkSqoPUY5NvQkwyqXu0VtpGoM/hOOTs1xjKmfkE2PVzVU1c/DKOsEXJ9dGu7n7VZ93Y6rEb4IqkXlpaaJoaw792j8U5PB3xDluHibHc6ymDiixLHYwLRtTcjmLiPUwm4IBIO62g37K0k45+F6rG3AYwtbBgwMEXkNQ8nv6LNMTy+XpkToEIY66Sx5jAL9TUP0RDiYKo0KvsQx6zsHGYY+Z2Uh7jVv0GOf4y6Qm7tk9obB+UtTqAQmUMPlLsjihl8+ryBnUiLaKTBTDNKzKXK04SE+0vIutGlDelMKTH3ZYAvBdBTxrB3MYo4asJWJocQTmat3onNxwSWHMxU8HLDEhpOaRFGIVv34yHVj8o7z8/p5dj/3p5nEBKNrJ/iGeqWlEZSCO6VsA7on6sjuyk80xJxanKX0M5S1eOnKE38hvikfaAmF3sTP4wNZH3C47DTFKw8uM93ZZ/Eh62A4xrJS7IEZ08ovg3rWWLwIGXDlUxwSAWaRzVFDc9eOV4YZ8gJ4zHXCICt69DnjJZtqFZ10FayUmn5ddJvSty3bbmvlobP9RLwQClGZLmU4pDjfLiCswZaZX6hhpBaRC9VQicRpNA4HZpU7WHB79C8plEHesAP5qgssXU4hdUaemE1A5Djn2wmM/v7NIhEV/xzZ20To0tACXiFiJvT1yLQ2xUf0Mt70nza+qG3LU5bu8jLdl+9ur7bF1ek6BPSXS49yP5tkQFQ3kPo/PIhI96NjRQlzpBdyc9zK17p5VuOvmrELXe67/5j6sVBUBYj2tvQtSbawaB79zVekIXnnpLrwfCfxpv51Oh3x1+eH5qQih5eZ50RrLmgz2rqj7k0gJI6F7kkwEFwy75rk6tM9rGSs4xqrZpb0KI77zRrAA6RsVVt4KzkyXaV4HIaEyG45IdqGJx2vsHgr7oWdOEaHEYCJhj9KRHy1J1g2MrPKvufFo44Kd7xZUOn5AGCayBkHp7tyG74TlCdTcDYJkvhyHTOxe/IvfRQ6Vo6rY/ufWHeVVaIZU8VEkz0lui4OtMrz9lmA85OLK2JTcNnwgb0oMuk2NcxrH9iS78f4f48ea423cffbd5dced0f885b770e'
        }
        cookies = {
            'guidesStatus':'off',
            'highContrastMode':'defaltMode',
            'cursorStatus':'off',
            'RAIL_EXPIRATION':self.rail_expiration,
            'RAIL_DEVICEID':self.rail_deviceid
        }
        resp = self.session.post(url, cookies=cookies, json=json_param)

        print('\npost_otn_logsdk_getinfo')
        print(resp.request.headers)
        print(resp.cookies)
        print(self.session.cookies)

        dic = json.loads(resp.text)
        self.fo = dic['data']['fo']
        print('fo:', self.fo)

    def post_passport_web_create_qrcode(self):
        url = 'https://kyfw.12306.cn/passport/web/create-qr64'
        data = {
            'appid':'otn'
        }
        cookies = {
            'guidesStatus':'off',
            'highContrastMode':'defaltMode',
            'cursorStatus':'off',
            'RAIL_DEVICEID':self.rail_deviceid,
            'RAIL_EXPIRATION':self.rail_expiration,
            'fo':self.fo
        }
        resp = self.session.post(url, data=data, cookies=cookies)

        print('\npost_passport_web_create_qrcode')
        print(resp.request.headers)
        print(resp.cookies)
        print(self.session.cookies)

        dic = json.loads(resp.text)
        self.uuid = dic['uuid']
        print('uuid:', self.uuid)

        image_bytes = base64.b64decode(dic['image'])
        with open(self.qrcode_filename, 'wb') as f:
            f.write(image_bytes)
        os.startfile(self.qrcode_filename)

        # qr = qrcode.QRCode(error_correction=qrcode.ERROR_CORRECT_L, box_size=5)
        # qr.add_data(image_bytes)
        # qr.print_ascii(invert=False)
        print('get qrcode success, please scan')

    def post_passport_web_checkqr(self):
        url = 'https://kyfw.12306.cn/passport/web/checkqr'
        while True:
            params = {
                'RAIL_DEVICEID':self.rail_deviceid,
                'RAIL_EXPIRATION':self.rail_expiration,
                'uuid':self.uuid,
                'appid':'otn'
            }
            cookies = {
                'guidesStatus':'off',
                'highContrastMode':'defaltMode',
                'cursorStatus':'off',
                'RAIL_DEVICEID':self.rail_deviceid,
                'RAIL_EXPIRATION':self.rail_expiration,
                'fo':self.fo
            }
            resp = self.session.post(url, params=params, cookies=cookies)
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
            time.sleep(2)

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
    ticket_object.get_otn_httpzf_getjs()
    ticket_object.get_otn_httpzf_logdevice()
    ticket_object.post_index_otn_login_conf()
    ticket_object.post_passport_web_auth_uamtk_static()
    ticket_object.post_otn_login_conf()
    ticket_object.post_otn_logsdk_getinfo()
    ticket_object.post_passport_web_create_qrcode()
    ticket_object.post_passport_web_checkqr()
    #ticket_object.auth_uamtk()
    #ticket_object.auth_uamauthclient()
    #ticket_object.initMy12306Api()
    #ticket_object.query_passengers()
