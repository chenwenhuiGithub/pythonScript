import requests
import json
import webwx


def tuling(req_text):
    req = {
        "reqType":0, # 0 -text, 1 - image, 2 - voice
        "perception":{
            "inputText":{
                "text":req_text
            },
            "selfInfo":{
                "location":{
                    "city":"杭州",
                    "province":"浙江",
                    "street":"延安路"
                }
            }
        },
        "userInfo":{
            "apiKey":"xxx", # apply apiKey from https://www.kancloud.cn/turing/www-tuling123-com/718227
            "userId":"xiaoming"
        }
    }

    resp = requests.request("post", 'http://openapi.turingapi.com/openapi/api/v2', json=req)
    dic = json.loads(resp.text)
    resp_text = dic["results"][0]["values"]["text"]
    return resp_text

def msg_handle(self, msg):
    if msg['senderType'] == 'CONTACT' and msg['contactRemarkName'] == u'老婆' and msg['msgType'] == 'TEXT':
        print(msg['contactRemarkName'])
        print('    ' + msg['content'])
        req_text = msg['content']
        resp_text = tuling(req_text)
        print('robot')
        print('    ' + resp_text)
        self.send_text(resp_text, msg['senderName'])


if __name__ == '__main__':
    weChat = webwx.webwx()
    weChat.register_msg_handle(msg_handle)
    weChat.login()
    weChat.run()
