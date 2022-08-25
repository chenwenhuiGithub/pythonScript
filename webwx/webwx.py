# -*- coding: utf-8 -*-
import os
import time
import re
import random
import xml.dom.minidom
import json
import html
import mimetypes
import hashlib
import pickle
import qrcode
import requests


def get_timestamp():
    return int(time.time() * 1000)

def get_rtimestamp():
    return -int(time.time())

def get_msgid():
    return str(get_timestamp()) + str(random.random())[2:6]

def get_md5(file_name):
    with open(file_name, mode='rb') as fptr:
        f_bytes = fptr.read()
    return hashlib.md5(f_bytes).hexdigest()


class webwx:
    def __init__(self, proxies=None):
        self.headers = { 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36' }    
        self.proxies = proxies
        self.session = requests.Session()
        self.uuid = ''
        self.redirect_uri = ''
        self.skey = ''
        self.sid = ''
        self.uin = ''
        self.pass_ticket = ''
        self.device_id = 'e' + repr(random.random())[2:17]
        self.base_request = {}
        self.sync_key = {}
        self.sync_key_str = ''
        self.account_self = {}
        self.account_contacts = {}
        self.account_subscriptions = {}
        self.account_groups = {}
        self.account_groups_members = {}
        self.index_upload_file = 0
        self.filename_pickle = 'webwx.pkl'

    def __get_uuid(self):
        url = 'https://login.weixin.qq.com/jslogin'
        params = {
            'appid':'wx782c26e4c19acffb',
            'redirect_uri':'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage',
            'fun':'new',
            'lang':'en_US',
            '_':get_timestamp()
        }
        resp = self.session.get(url, params=params, headers=self.headers, proxies=self.proxies)
        regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)";'
        data = re.search(regx, resp.text)
        if data.group(1) == '200':
            self.uuid = data.group(2)
            print('get uuid success:%s' %self.uuid)
        else:
            print('get uuid failed')

    def __gen_qrcode(self):
        url = 'https://login.weixin.qq.com/l/' + self.uuid
        code = qrcode.QRCode()
        code.add_data(url)
        code.print_ascii(invert=False)
        print('gen qrcode success, please scan')

    def __login(self):
        url = 'https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login'
        tip = 1 # 0-scaned, 1-not scaned

        while True:
            params = {
                'loginicon':'true',
                'uuid':self.uuid,
                'tip':tip,
                'r':get_rtimestamp(),
                '_':get_timestamp()
            }
            resp = self.session.get(url, params=params, headers=self.headers, proxies=self.proxies)
            data = re.search(r'window.code=(\d+)', resp.text)
            if data.group(1) == '408': # timeout
                tip = 1
                print('login failed, scan timeout')
            elif data.group(1) == '201': # scaned
                tip = 0
                print('scan success, logining...')
            elif data.group(1) == '200': # success
                param = re.search(r'window.redirect_uri="(\S+?)";', resp.text)
                self.redirect_uri = param.group(1)
                print('redirect_uri:%s' %self.redirect_uri)
                return
            else:
                print('login failed, unknown status:%s' %data.group(1))
                return
            time.sleep(1)

    def __get_params(self):
        url = self.redirect_uri + '&fun=new&version=v2'
        resp = self.session.get(url, headers=self.headers, allow_redirects=False, proxies=self.proxies)
        nodes = xml.dom.minidom.parseString(resp.text).documentElement.childNodes
        for node in nodes:
            if node.nodeName == 'skey':
                self.skey = node.childNodes[0].data
                self.base_request['Skey'] = self.skey
                print('skey:%s' %self.skey)
            elif node.nodeName == 'wxsid':
                self.sid = node.childNodes[0].data
                self.base_request['Sid'] = self.sid
                print('sid:%s' %self.sid)
            elif node.nodeName == 'wxuin':
                self.uin = node.childNodes[0].data
                self.base_request['Uin'] = self.uin
                print('uin:%s' %self.uin)
            elif node.nodeName == 'pass_ticket':
                self.pass_ticket = node.childNodes[0].data
                print('pass_ticket:%s' %self.pass_ticket)
        self.base_request['DeviceID'] = self.device_id
        print('device_id:%s' %self.device_id)

    def __initinate(self):
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit'
        params = {
            'r':get_rtimestamp(),
            'pass_ticket':self.pass_ticket
        }
        data = {
            'BaseRequest':self.base_request
        }
        headers = {
            'ContentType':'application/json; charset=UTF-8',
            'User-Agent':self.headers['User-Agent']
        }
        resp = self.session.post(url, params=params, data=json.dumps(data), headers=headers, proxies=self.proxies)
        resp.encoding = 'utf-8'
        dic = json.loads(resp.text)
        self.sync_key = dic['SyncKey']
        self.sync_key_str = '|'.join([str(item['Key']) + '_' + str(item['Val']) for item in self.sync_key['List']])
        self.account_self = dic['User']
        print('sync_key:%s' %self.sync_key)
        print('sync_key_str:%s' %self.sync_key_str)
        print('account_self:%s' %self.account_self)

    def __status_notify(self):
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxstatusnotify'
        params = {
            'pass_ticket':self.pass_ticket
        }
        self.base_request['Uin'] = int(self.base_request['Uin'])
        data = {
            'BaseRequest':self.base_request,
            'ClientMsgId':get_timestamp(),
            'Code':3,
            'FromUserName':self.account_self['UserName'],
            'ToUserName':self.account_self['UserName']
        }
        headers = {
            'ContentType':'application/json; charset=UTF-8',
            'User-Agent':self.headers['User-Agent']
        }
        self.session.post(url, params=params, data=json.dumps(data), headers=headers, proxies=self.proxies)

    def __get_contact(self):
        member_list = []
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact'
        params = {
            'pass_ticket':self.pass_ticket,
            'r':get_timestamp(),
            'seq':0,
            'skey':self.skey
        }
        headers = {
            'ContentType':'application/json; charset=UTF-8',
            'User-Agent':self.headers['User-Agent']
        }
        resp = self.session.post(url, params=params, headers=headers, timeout=180, proxies=self.proxies)
        resp.encoding = 'utf-8'
        dic = json.loads(resp.text)
        member_list.extend(dic['MemberList'])

        while dic['Seq'] != 0:
            params['seq'] = dic['Seq']
            resp = self.session.post(url, params=params, headers=headers, timeout=180, proxies=self.proxies)
            resp.encoding = 'utf-8'
            dic = json.loads(resp.text)
            member_list.extend(dic['MemberList'])

        for member in member_list:
            if member['UserName'].find('@@') != -1:
                self.account_groups[member['UserName']] = member # not include detail members info
            elif member['VerifyFlag'] & 8 != 0:
                self.account_subscriptions[member['UserName']] = member # include weixin,weixinzhifu
            else:
                self.account_contacts[member['UserName']] = member # include filehelper

        print('num subscriptions:%d' %len(self.account_subscriptions))
        print('num groups:%d' %len(self.account_groups))
        print('num contacts:%d' %len(self.account_contacts))

    def __get_group_members(self):
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxbatchgetcontact'
        params = {
            'type':'ex',
            'r':get_timestamp(),
            'lang':'en_US'
        }

        grouplist = []
        for group in self.account_groups.values():
            grouplist.append({'UserName':group['UserName'], 'ChatRoomId':group['ChatRoomId']})

        data = {
            'BaseRequest':self.base_request,
            'Count':len(self.account_groups),
            'List':grouplist
        }
        headers = {
            'ContentType':'application/json; charset=UTF-8',
            'User-Agent':self.headers['User-Agent']
        }
        resp = self.session.post(url, params=params, data=json.dumps(data), headers=headers, timeout=180, proxies=self.proxies)
        resp.encoding = 'utf-8'
        dic = json.loads(resp.text)
        for member in dic['ContactList']:
            self.account_groups_members[member['UserName']] = member # save group member list info

    def __sync_check(self):
        url = 'https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck'
        params = {
            'r':get_timestamp(),
            'skey':self.skey,
            'sid':self.sid,
            'uin':self.uin,
            'deviceid':self.device_id,
            'synckey':self.sync_key_str,
            '_':get_timestamp()
        }
        resp = self.session.get(url, params=params, headers=self.headers, proxies=self.proxies)
        data = re.search(r'window.synccheck=\{retcode:"(\d+)",selector:"(\d+)"\}', resp.text)
        retcode = data.group(1)
        selector = data.group(2)
        return retcode, selector

    def __webwx_sync(self):
        msg_list = []
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsync'
        params = {
            'sid':self.sid,
            'skey':self.skey,
            'pass_ticket':self.pass_ticket
        }
        data = {
            'BaseRequest':self.base_request,
            'SyncKey':self.sync_key,
            'rr':get_rtimestamp()
        }
        headers = {
            'ContentType':'application/json; charset=UTF-8',
            'User-Agent':self.headers['User-Agent']
        }
        resp = self.session.post(url, params=params, data=json.dumps(data), headers=headers, proxies=self.proxies)
        resp.encoding = 'utf-8'
        dic = json.loads(resp.text)
        if dic['BaseResponse']['Ret'] == 0:
            self.sync_key = dic['SyncKey']
            self.sync_key_str = '|'.join([str(keyVal['Key']) + '_' + str(keyVal['Val']) for keyVal in self.sync_key['List']])
            msg_list = dic['AddMsgList']
        return msg_list

    def __parse_group_msg(self, msg, parsed_msg):
        parsed_msg['userNickName'] = ''
        parsed_msg['userDisplayName'] = ''
        parsed_msg['isAtMe'] = False

        found_flag1 = False
        found_flag2 = False
        ret = re.match('(@[0-9a-z]*?):<br/>(.*)$', msg['Content']) # username:<br>text
        user_name, text = ret.groups()
        for item in self.account_groups_members[msg['FromUserName']]['MemberList']:
            if item['UserName'] == user_name:
                parsed_msg['userNickName'] = item['NickName']
                parsed_msg['userDisplayName'] = item['DisplayName']
                found_flag1 = True

            if item['UserName'] == self.account_self['UserName']:
                my_displayname_in_group = item['DisplayName']
                found_flag2 = True

            if found_flag1 and found_flag2:
                break

        str_at = '@' + self.account_self['NickName'] + '\u2005'
        if my_displayname_in_group:
            str_at = '@' + my_displayname_in_group + '\u2005'

        if text.find(str_at) != -1:
            parsed_msg['isAtMe'] = True

    def __parse_msg(self, msg):
        parsed_msg = {}
        parsed_msg['senderType'] = 'UNSUPPORTED'
        parsed_msg['senderName'] = msg['FromUserName']
        parsed_msg['msgType'] = 'UNSUPPORTED'
        parsed_msg['msgId'] = msg['MsgId']

        if self.account_groups.__contains__(msg['FromUserName']):
            parsed_msg['senderType'] = 'GROUP'
            parsed_msg['groupNickName'] = self.account_groups[msg['FromUserName']]['NickName']
            self.__parse_group_msg(msg, parsed_msg) # parse userNickName/userDisplayName/isAtMe
        elif self.account_subscriptions.__contains__(msg['FromUserName']):
            parsed_msg['senderType'] = 'SUBSCRIPTION'
            parsed_msg['subscriptionNickName'] = self.account_subscriptions[msg['FromUserName']]['NickName']
        elif self.account_contacts.__contains__(msg['FromUserName']):
            parsed_msg['senderType'] = 'CONTACT'
            parsed_msg['contactNickName'] = self.account_contacts[msg['FromUserName']]['NickName']
            parsed_msg['contactRemarkName'] = self.account_contacts[msg['FromUserName']]['RemarkName']
        elif self.account_self['UserName'] == msg['FromUserName']:
            parsed_msg['senderType'] = 'MYSELF'
            parsed_msg['myNickName'] = self.account_self['NickName']

        msg_type = msg['MsgType']
        if msg_type == 1: # text/link/position
            sub_msg_type = msg['SubMsgType']
            if sub_msg_type == 0: # text/link
                parsed_msg['msgType'] = 'TEXT'
                parsed_msg['content'] = msg['Content']
                if parsed_msg['senderType'] == 'GROUP':
                    ret = re.match('(@[0-9a-z]*?):<br/>(.*)$', msg['Content'])
                    parsed_msg['content'] = ret.groups()[1] # delete sender username info
            elif sub_msg_type == 48: # position
                parsed_msg['msgType'] = 'POSITION'
                doc = xml.dom.minidom.parseString(msg['OriContent']).documentElement
                node = doc.getElementsByTagName('location')[0]
                parsed_msg['x'] = node.getAttribute('x')
                parsed_msg['y'] = node.getAttribute('y')
                parsed_msg['scale'] = node.getAttribute('scale')
                parsed_msg['label'] = node.getAttribute('label')
                parsed_msg['poiname'] = node.getAttribute('poiname')
        elif msg_type == 3: # image
            parsed_msg['msgType'] = 'IMAGE'
            parsed_msg['mediaId'] = msg['MsgId']
            parsed_msg['imgHeight'] = msg['ImgHeight']
            parsed_msg['imgWidth'] = msg['ImgWidth']
            parsed_msg['downloadFunc'] = self.__img_download
        elif msg_type == 34: # voice
            parsed_msg['msgType'] = 'VOICE'
            parsed_msg['mediaId'] = msg['MsgId']
            parsed_msg['voiceLength'] = msg['VoiceLength']
            parsed_msg['downloadFunc'] = self.__voice_download
        elif msg_type == 42: # card
            parsed_msg['msgType'] = 'CARD'
            content = html.unescape(msg['Content']) # TODO: delete emoji info
            content = content.replace('<br/>', '\n')
            doc = xml.dom.minidom.parseString(content).documentElement
            parsed_msg['username'] = doc.getAttribute('username')
            parsed_msg['nickname'] = doc.getAttribute('nickname')
            parsed_msg['alias'] = doc.getAttribute('alias')
            parsed_msg['province'] = doc.getAttribute('province')
            parsed_msg['city'] = doc.getAttribute('city')
            parsed_msg['sex'] = doc.getAttribute('sex')
            parsed_msg['regionCode'] = doc.getAttribute('regionCode')
        elif msg_type == 43: # video
            parsed_msg['msgType'] = 'VIDEO'
            parsed_msg['mediaId'] = msg['MsgId']
            parsed_msg['playLength'] = msg['PlayLength']
            parsed_msg['imgHeight'] = msg['ImgHeight']
            parsed_msg['imgWidth'] = msg['ImgWidth']
            parsed_msg['downloadFunc'] = self.__video_download
        elif msg_type == 47: # animation
            parsed_msg['msgType'] = 'ANIMATION'
            parsed_msg['imgHeight'] = msg['ImgHeight']
            parsed_msg['imgWidth'] = msg['ImgWidth']
        elif msg_type == 49: # attachment
            app_msg_type = msg['AppMsgType']
            if app_msg_type == 6: # file
                parsed_msg['msgType'] = 'FILE'
                parsed_msg['mediaId'] = msg['MediaId']
                parsed_msg['fileName'] = msg['FileName']
                parsed_msg['encryFileName'] = msg['EncryFileName']
                parsed_msg['fileSize'] = msg['FileSize']
                parsed_msg['downloadFunc'] = self.__file_download
        elif msg_type == 10002: # revoke
            parsed_msg['msgType'] = 'REVOKE'
            parsed_msg['revokedMsgId'] = re.search('&lt;msgid&gt;(.*?)&lt;', msg['Content']).group(1)

        return parsed_msg

    def __handle_msg(self, msg):
        print(msg)

    def __img_download(self, msg):
        media_id = msg['mediaId']
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetmsgimg?MsgID=%s&skey=%s'%(media_id, self.skey)
        resp = self.session.get(url, stream=True, headers=self.headers, proxies=self.proxies)
        file_name = 'img_' + media_id + '.jpg'
        with open(file_name, 'wb') as fptr:
            fptr.write(resp.content)
        print('download img success:%s' %file_name)

    def __voice_download(self, msg):
        media_id = msg['mediaId']
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetvoice?msgID=%s&skey=%s'%(media_id, self.skey)
        resp = self.session.get(url, stream=True, headers=self.headers, proxies=self.proxies)
        file_name = 'voice_' + media_id + '.mp3'
        with open(file_name, 'wb') as fptr:
            fptr.write(resp.content)
        print('download voice success:%s' %file_name)

    def __video_download(self, msg):
        media_id = msg['mediaId']
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetvideo?msgID=%s&skey=%s'%(media_id, self.skey)
        headers = {
            'Range':'bytes=0-',
            'User-Agent':self.headers['User-Agent']
        }
        resp = self.session.get(url, stream=True, headers=headers, proxies=self.proxies)
        file_name = 'video_' + media_id + '.mp4'
        with open(file_name, 'wb') as fptr:
            fptr.write(resp.content)
        print('download video success:%s' %file_name)

    def __file_download(self, msg):
        url = 'https://file.wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetmedia'
        params = {
            'sender':msg['senderName'],
            'mediaid':msg['mediaId'],
            'encryfilename':msg['encryFileName'],
            'fromuser':self.uin,
            'pass_ticket':self.pass_ticket,
            'webwx_data_ticket':self.session.cookies['webwx_data_ticket']
        }
        resp = self.session.get(url, params=params, stream=True, headers=self.headers, proxies=self.proxies)
        with open(msg['fileName'], 'wb') as fptr:
            fptr.write(resp.content)
        print('download file success:%s' %msg['fileName'])

    def __save_pickle(self):
        conf = {
            'skey':self.skey,
            'sid':self.sid,
            'uin':self.uin,
            'pass_ticket':self.pass_ticket,
            'device_id':self.device_id,
            'base_request':self.base_request,
            'sync_key':self.sync_key,
            'sync_key_str':self.sync_key_str,
            'account_self':self.account_self,
            'account_contacts':self.account_contacts,
            'account_subscriptions':self.account_subscriptions,
            'account_groups':self.account_groups,
            'account_groups_members':self.account_groups_members,
            'cookies':self.session.cookies.get_dict()
        }

        with open(self.filename_pickle, 'wb') as fptr:
            fptr.truncate() # clean file
            pickle.dump(conf, fptr)

    def __load_pickle(self):
        if os.path.exists(self.filename_pickle):
            with open(self.filename_pickle, 'rb') as fptr:
                conf = pickle.load(fptr)

            self.skey = conf['skey']
            self.sid = conf['sid']
            self.uin = conf['uin']
            self.pass_ticket = conf['pass_ticket']
            self.device_id = conf['device_id']
            self.base_request = conf['base_request']
            self.sync_key = conf['sync_key']
            self.sync_key_str = conf['sync_key_str']
            self.account_self = conf['account_self']
            self.account_contacts = conf['account_contacts']
            self.account_subscriptions = conf['account_subscriptions']
            self.account_groups = conf['account_groups']
            self.account_groups_members = conf['account_groups_members']
            self.session.cookies = requests.utils.cookiejar_from_dict(conf['cookies'])
            return True
        return False

    def __delete_pickle(self):
        if os.path.exists(self.filename_pickle):
            os.remove(self.filename_pickle)

    def __get_username(self, name):
        if self.account_contacts.__contains__(name) or self.account_groups.__contains__(name): # input contact/group UserName
            return name

        for value in self.account_contacts.values(): # input contact NickName/RemarkName
            if name in (value['NickName'], value['RemarkName']):
                return value['UserName']

        for value in self.account_groups.values(): # input group NickName
            if value['NickName'] == name:
                return value['UserName']

    def __upload_media(self, file_name, media_type, to_user_name):
        url = 'https://file.wx.qq.com/cgi-bin/mmwebwx-bin/webwxuploadmedia?f=json'
        file_len = os.path.getsize(file_name)
        file_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
        md5 = get_md5(file_name)
        files = {
            'id':(None, 'WU_FILE_%s' % str(self.index_upload_file)),
            'name':(None, os.path.basename(file_name)),
            'type':(None, file_type),
            'lastModifiedDate':(None, '%s' % time.ctime(os.path.getmtime(file_name))),
            'size':(None, str(file_len)),
            'mediatype':(None, media_type),
            'uploadmediarequest':(None, json.dumps({
                'UploadType':2,
                'BaseRequest':self.base_request,
                'ClientMediaId':get_msgid(),
                'TotalLen':str(file_len),
                'StartPos':0,
                'DataLen':str(file_len),
                'MediaType':4,
                'FromUserName':self.account_self['UserName'],
                'ToUserName':to_user_name,
                'FileMd5':md5
            })),
            'webwx_data_ticket':(None, self.session.cookies['webwx_data_ticket']),
            'pass_ticket':(None, self.pass_ticket),
        }

        fptr = open(file_name, 'rb')
        chunks = int((file_len - 1) / (1 << 19)) + 1 # one time upload 524288 bytes
        if chunks > 1:
            for chunk in range(chunks):
                f_bytes = fptr.read(1 << 19)
                files['chunks'] = (None, str(chunks))
                files['chunk'] = (None, str(chunk))
                files['filename'] = (os.path.basename(file_name), f_bytes, file_type.split('/')[1])
                resp = self.session.post(url, files=files, headers=self.headers, proxies=self.proxies)
        else:
            f_bytes = fptr.read(1 << 19)
            files['filename'] = (os.path.basename(file_name), f_bytes, file_type.split('/')[1])
            resp = self.session.post(url, files=files, headers=self.headers, proxies=self.proxies)
        dic = json.loads(resp.text)
        fptr.close()
        self.index_upload_file += 1

        return dic['MediaId']

    def __send_media(self, url, file_name, media_type, receiver):
        params = {
            'fun':'async',
            'f':'json',
            'lang':'en_US',
            'pass_ticket':self.pass_ticket
        }

        msg_id = get_msgid()
        to_user_name = self.__get_username(receiver)
        data = {
            'BaseRequest':self.base_request,
            'Msg':{
                'ClientMsgId':msg_id,
                'FromUserName':self.account_self['UserName'],
                'LocalID':msg_id,
                'ToUserName':to_user_name,
            },
            'Scene':0
        }

        media_id = self.__upload_media(file_name, media_type, to_user_name)

        if media_type == 'pic':
            data['Msg']['Content'] = ''
            data['Msg']['MediaId'] = media_id
            data['Msg']['Type'] = 3
        elif media_type == 'video':
            data['Msg']['Content'] = ''
            data['Msg']['MediaId'] = media_id
            data['Msg']['Type'] = 43
        elif media_type == 'doc':
            file_len = os.path.getsize(file_name)
            content = ("<appmsg appid='wxeb7ec651dd0aefa9' sdkver=''><title>%s</title>" % os.path.basename(file_name) +
                "<des></des><action></action><type>6</type><content></content><url></url><lowurl></lowurl>" +
                "<appattach><totallen>%s</totallen><attachid>%s</attachid>" % (str(file_len), media_id) +
                "<fileext>%s</fileext></appattach><extinfo></extinfo></appmsg>" % os.path.splitext(file_name)[1].replace('.', ''))
            data['Msg']['Content'] = content
            data['Msg']['Type'] = 6

        headers = {
            'ContentType':'application/json; charset=UTF-8',
            'User-Agent':self.headers['User-Agent']
        }
        self.session.post(url, params=params, data=json.dumps(data), headers=headers, proxies=self.proxies)

    def send_text(self, text, receiver):
        ''' send text to receiver, receiver can be msg['senderName']/nickname/remarkname '''
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg'
        params = {
            'pass_ticket':self.pass_ticket
        }
        msg_id = get_msgid()
        to_username = self.__get_username(receiver)
        data = {
            'BaseRequest':self.base_request,
            'Msg':{
                "ClientMsgId":msg_id,
                "Content":text,
                "FromUserName":self.account_self['UserName'],
                "LocalID":msg_id,
                "ToUserName":to_username,
                "Type":1
            },
            'Scene':0
        }
        headers = {
            'ContentType':'application/json; charset=UTF-8',
            'User-Agent':self.headers['User-Agent']
        }
        self.session.post(url, params=params, data=json.dumps(data, ensure_ascii=False).encode('utf8'), headers=headers, proxies=self.proxies)

    def send_image(self, file_name, receiver):
        ''' send image to receiver, receiver can be msg['senderName']/nickname/remarkname '''
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsgimg'
        self.__send_media(url, file_name, 'pic', receiver)

    def send_video(self, file_name, receiver):
        ''' send video to receiver, receiver can be msg['senderName']/nickname/remarkname '''
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendvideomsg'
        self.__send_media(url, file_name, 'video', receiver)

    def send_file(self, file_name, receiver):
        ''' send file to receiver, receiver can be msg['senderName']/nickname/remarkname '''
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendappmsg'
        self.__send_media(url, file_name, 'doc', receiver)

    def register_msg_handle(self, func):
        """ register custom handle to handle msg, default handle just print msg info """
        webwx.__handle_msg = func

    def login(self, enable_relogin=True):
        """ scan qrcode or hot relogin without scan """
        if enable_relogin == False or self.__load_pickle() == False:
            self.__get_uuid()
            self.__gen_qrcode()
            self.__login()
            self.__get_params()
            self.__initinate()
            self.__status_notify()
            self.__get_contact()
            self.__get_group_members()
            if enable_relogin:
                self.__save_pickle()
        print('login success')

    def logout(self):
        """ logout """
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxlogout'
        params = {
            'redirect':1,
            'type':0,
            'skey':self.skey
        }
        data = {
            'sid':self.sid,
            'uin':self.uin
        }
        headers = {
            'ContentType':'application/json; charset=UTF-8',
            'User-Agent':self.headers['User-Agent']
        }
        self.session.post(url, params=params, data=json.dumps(data), headers=headers, proxies=self.proxies)

        self.__delete_pickle()
        print('logout success')

    def run(self):
        """ loop receive and process messages """
        handle_enable = True

        while True:
            retcode, selector = self.__sync_check()
            if retcode == '0':
                if selector == '2': # recv new msg
                    msg_list = self.__webwx_sync()
                    for msg in msg_list:
                        parsed_msg = self.__parse_msg(msg)
                        if parsed_msg['senderType'] == 'MYSELF' and parsed_msg['msgType'] == 'TEXT':
                            if parsed_msg['content'] == 'enable':
                                handle_enable = True
                                print('enable msg handle')
                                continue
                            elif parsed_msg['content'] == 'disable':
                                handle_enable = False
                                print('disable msg handle')
                                continue
                            elif parsed_msg['content'] == 'logout':
                                self.logout()
                                return

                        if handle_enable:
                            self.__handle_msg(parsed_msg)
            elif retcode == '1101': # logout by phone
                self.__delete_pickle()
                print('logout success')
                return
            else:
                print('unsupported retcode:%s' %retcode)
            time.sleep(1)
