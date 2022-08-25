import time
import threading
import webwx


queue_msgs = {}

def msg_handle(self, msg):
    if msg['msgType'] == 'TEXT':
        msg['life'] = 120
        queue_msgs[msg['msgId']] = msg

    if msg['msgType'] == 'REVOKE':
        revoked_msg = queue_msgs[msg['revokedMsgId']]
        if revoked_msg['senderType'] == 'GROUP':
            if revoked_msg['userDisplayName']:
                print(revoked_msg['groupNickName'] + ' - ' + revoked_msg['userDisplayName'])
            else:
                print(revoked_msg['groupNickName'] + ' - ' + revoked_msg['userNickName'])
        elif revoked_msg['senderType'] == 'CONTACT':
            if revoked_msg['contactRemarkName']:
                print(revoked_msg['contactRemarkName'])
            else:
                print(revoked_msg['contactNickName'])
        else:
            print('unknown')
        print('    ' + revoked_msg['content'])

def clean_msgs():
    while True:
        keys = list(queue_msgs.keys())
        for key in keys:
            queue_msgs[key]['life'] -= 1
            if queue_msgs[key]['life'] == 0:
                del queue_msgs[key]
        time.sleep(1)


if __name__ == '__main__':
    threading.Thread(target=clean_msgs).start()

    weChat = webwx.webwx()
    weChat.register_msg_handle(msg_handle)
    weChat.login()
    weChat.run()
