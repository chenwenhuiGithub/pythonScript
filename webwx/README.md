# webwx

```webwx``` 是一个开源的微信客户端实现接口，使用 python 完成微信的登录和消息收发功能

当前支持的功能相对基础，后续会持续新增功能并优化

具体协议分析参考博客：https://blog.csdn.net/chenwh_cn/article/details/108581139


## API 接口函数

### login(enable_relogin=True):
```python
enable_relogin:
True:  使用缓存，每次登录成功后将信息保存到文件，如果缓存仍然有效则下次无需再扫码登录，可以直接收发消息
False: 不使用缓存，每次都扫码登录
默认值 True，即默认使用缓存
```

### logout():
```python
退出登录
```

### send_text(text, receiver):
```python
发送普通文本消息，receiver 可以取值 msg['senderName']/联系人昵称/联系人备注名/群组昵称，并按照这个顺序优先查找
```

### send_image(file_name, receiver):
```python
发送 .jpg 格式图片，receiver 可以取值 msg['senderName']/联系人昵称/联系人备注名/群组昵称，并按照这个顺序优先查找
```

### send_video(file_name, receiver):
```python
发送 .mp4 格式视频，receiver 可以取值 msg['senderName']/联系人昵称/联系人备注名/群组昵称，并按照这个顺序优先查找
```

### send_file(file_name, receiver):
```python
发送普通文件，receiver 可以取值 msg['senderName']/联系人昵称/联系人备注名/群组昵称，并按照这个顺序优先查找
```

### register_msg_handle(func):
```python
注册自定义消息处理函数，默认处理是打印消息内容
```

### run():
```python
1. 检查是否有接收到新消息
2. 解析消息，不同消息类型解析出不同字段信息
3. 调用默认的或自定义的消息处理函数处理消息

注意: 通过在 'filehelper' 中发送命令可以进行系统控制
1. 'enable': 打开消息处理
2. 'disable': 关闭消息处理
3. 'logout': 退出登录，程序退出
```


## 基本使用示例

```python
import webwx

weChat = webwx.webwx()
weChat.login()
weChat.run()
```

该示例实现最基础功能：微信二维码扫码登录或者缓存自动登录，然后接收并解析消息，最后调用默认消息处理函数处理消息


## 自定义消息处理

```python
import webwx

# 自定义消息处理函数
def msg_handle(self, msg):
    if msg['msgType'] == 'TEXT':
        if msg['senderType'] == 'GROUP':
            if msg['userDisplayName']:
                print(msg['groupNickName'] + ' - ' + msg['userDisplayName'])
            else:
                print(msg['groupNickName'] + ' - ' + msg['userNickName'])
        elif msg['senderType'] == 'CONTACT':
            if msg['contactRemarkName']:
                print(msg['contactRemarkName'])
            else:
                print(msg['contactNickName'])
        elif msg['senderType'] == 'MYSELF':
            print(msg['myNickName'])
        else:
            print('unknown')
        print('    ' + msg['content'])


weChat = webwx.webwx()
weChat.register_msg_handle(msg_handle)
weChat.login()
weChat.run()
```

调用 ```register_msg_handle```，用自定义消息处理函数替换默认处理函数

```msg``` 即解析后的消息，字典类型，消息类型不同所包含的字段也不同，有些字段是必有的，有些是可选的

### 必有字段：

```python
'senderType': 字符串类型，取值 "GROUP/SUBSCRIPTION/CONTACT/MYSELF/UNSUPPORTED", 表示消息来源于群组/公众号/联系人/自己/不支持

'senderName': 字符串类型，表示发送者的身份，由系统分配，@@开头表示群组，@开头表示联系人或者公众号

'msgType': 字符串类型，取值 "TEXT/POSITION/IMAGE/VOICE/VIDEO/CARD/ANIMATION/FILE/REVOKE/UNSUPPORTED", 表示消息类型是文本/位置/图片/语音/视频/名片/表情/文件/撤回/不支持

'msgId': 字符串类型，表示消息的唯一 id，由系统分配
```

### 可选字段：

```python
senderType = GROUP

    'groupNickName': 字符串类型，表示发送者所在的群组昵称
    'userNickName': 字符串类型， 表示发送者的昵称
    'userDisplayName': 字符串类型，表示发送者设置的自己在该群的显示名称，没有设置为 ''
    'meIsAt': 布尔类型，表示自己是否被群组消息 @


senderType = SUBSCRIPTION

    'subscriptionNickName': 字符串类型，表示发送者公众号昵称


senderType = CONTACT

    'contactNickName':   字符串类型，表示发送者昵称
    'contactRemarkName': 字符串类型，表示发送者备注名


senderType = MYSELF

    'myNickName': 字符串类型，表示自己的昵称


msgType = TEXT:

    'content': 字符串类型，表示接收到的消息内容


msgType = POSITION:

    'x': 字符串类型，浮点数，表示纬度

    'y': 字符串类型，浮点数，表示经度

    'scale': 字符串类型，整数，表示缩放比例

    'label': 字符串类型，表示位置的标签名称

    'poiname': 字符串类型，表示位置的具体名称


msgType = IMAGE:

    'imgHeight': 整数类型，表示图片高度

    'imgWidth': 整数类型，表示图片宽度

    'mediaId': 字符串类型，表示图片在服务器的资源 id，由系统分配，用于下载使用

    'downloadFunc': 函数类型，表示下载图片的函数

    调用 msg['downloadFunc'](msg)，将下载图片到当前目录，保存文件名为 img_(mediaId).jpg


msgType = VOICE:

    'voiceLength': 整数类型，表示语音时长，单位毫秒

    'mediaId': 字符串类型，表示图片在服务器的资源 id，由系统分配，用于下载使用

    'downloadFunc': 函数类型，表示下载语音的函数

    调用 msg['downloadFunc'](msg)，将下载语音到当前目录，保存文件名为 voice_(mediaId).mp3


msgType = VIDEO:

    'imgHeight': 整数类型，表示视频高度

    'imgWidth': 整数类型，表示视频宽度

    'playLength': 整数类型，表示视频时长，单位秒

    'mediaId': 字符串类型，表示视频在服务器的资源 id，由系统分配，用于下载使用

    'downloadFunc': 函数类型，表示下载视频的函数

    调用 msg['downloadFunc'](msg)，将下载视频到当前目录，保存文件名为 video_(mediaId).mp4


msgType = CARD:

    'username': 字符串类型，表示微信号

    'nickname': 字符串类型，表示昵称

    'alias': 字符串类型，表示别名

    'province': 字符串类型，表示省

    'city': 字符串类型，表示城市

    'sex': 字符串类型，表示性别，0-未知 1-男 2-女

    'regionCode': 字符串类型，表示注册地


msgType = ANIMATION:

    'imgHeight': 整数类型，表示表情高度

    'imgWidth': 整数类型，表示表情宽度


msgType = FILE:

    'fileName': 字符串类型，表示文件名

    'encryFileName': 字符串类型，表示 encry 文件名

    'fileSize': 字符串类型，表示文件大小，单位字节

    'mediaId': 字符串类型，表示视频多媒体 id，由系统分配，用于下载使用

    'downloadFunc': 函数类型，表示下载文件的函数

    调用 msg['downloadFunc'](msg)，将下载文件到当前目录，保存文件名为 'fileName' 字段值

msgType = REVOKE:

    'revokedMsgId': 字符串类型，表示被撤回的那条消息的 id


msgType = UNSUPPORTED:

    没有可选字段
```


## 进阶应用

### 使用代理
在 webwx 的构造函数中传入代理，使用代理完成 GET/POST 请求

```python
proxies = { 'http':'http://ip:port', 'https':'https://ip:port' }
weChat = webwx.webwx(proxies=proxies)
```


### 下载多媒体资源
完整代码请参考: https://blog.csdn.net/chenwh_cn/article/details/108794650

```python
# 下载接收到的图片/语音/视频/普通文件，保存为 .jpg/.mp3/.mp4/.xxx 文件到当前目录
def msg_handle(self, msg):
    if msg['msgType'] in ["IMAGE", "VOICE", "VIDEO", "FILE"]:
        msg['downloadFunc'](msg)
```


### 智能聊天机器人
完整代码请参考: https://blog.csdn.net/chenwh_cn/article/details/108663666

```python
EMOTIBOT_API_ID = "xxx" # 申请的 API_ID
EMOTIBOT_API_URL = "http://idc.emotibot.com/api/ApiKey/openapi.php"

TULING_API_KEY = "xxx"  # 申请的 API_KEY
TULING_API_URL = "http://openapi.tuling123.com/openapi/api/v2"

def emotibot(req_text):
    params = {
        "cmd":"chat",
        "appid":EMOTIBOT_API_ID,
        "userid":"xiaoming",
        "text":req_text,
        "location":"hangzhou"
    }

    resp = requests.request("post", EMOTIBOT_API_URL, params=params)
    dic = json.loads(resp.text)
    resp_text = dic["data"][0]["value"]
    return resp_text

def tuling(req_text):
    req = {
        "reqType":0,
        "perception":{
            "inputText":{
                "text":req_text
            },
            "selfInfo":{
                "location":{
                    "city":"hangzhou",
                    "province":"zhejiang",
                    "street":"dongxin street"
                }
            }
        },
        "userInfo":{
            "apiKey":TULING_API_KEY,
            "userId":"xiaoming"
        }
    }

    resp = requests.request("post", TULING_API_URL, json=req)
    dic = json.loads(resp.text)
    resp_text = dic["results"][0]["values"]["text"]
    return resp_text

def msg_handle(self, msg):
    if msg['senderType'] == 'CONTACT' and msg['contactRemarkName'] == u'张三' and msg['msgType'] == 'TEXT':
        req_text = msg['content']
        # resp_text = emotibot(req_text)
        resp_text = tuling(req_text)
        self.send_text(resp_text, msg['senderName'])
```


### 监测自己被群组 @ 消息
完整代码请参考: https://blog.csdn.net/chenwh_cn/article/details/108774217

```python
def msg_handle(self, msg):
    if msg['senderType'] == 'GROUP' and msg['msgType'] == 'TEXT' and msg['meIsAt'] == True:
        self.send_text(msg['content'], 'filehelper')
```


### 监测撤回的消息
完整代码请参考: https://blog.csdn.net/chenwh_cn/article/details/108797745

```python
queue_msgs = {}

def msg_handle(self, msg):
    if msg['msgType'] == 'TEXT':
        msg['life'] = 120
        queue_msgs[msg['msgId']] = msg

    if msg['msgType'] == 'REVOKE':
        revoked_msg = queue_msgs[msg['revokedMsgId']]
        # self.send_text(revoked_msg['content'], revoked_msg['senderName']) # 撤回的内容发回给发送方
        self.send_text(revoked_msg['content'], 'filehelper') # 撤回的内容发送到 filehelper

def clean_msgs():
    while True:
        keys = list(queue_msgs.keys())
        for key in keys:
            queue_msgs[key]['life'] -= 1
            if queue_msgs[key]['life'] == 0:
                del queue_msgs[key]
        time.sleep(1)


threading.Thread(target=clean_msgs).start()

weChat = webwx.webwx()
weChat.register_msg_handle(msg_handle)
weChat.login()
weChat.run()
```


## 待实现功能

1. 优化缓存，提高加载效率
2. emoji 表情内容过滤
3. 增加异常处理
