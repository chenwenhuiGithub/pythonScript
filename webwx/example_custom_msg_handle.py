import webwx


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


if __name__ == '__main__':
    weChat = webwx.webwx()
    weChat.register_msg_handle(msg_handle)
    weChat.login()
    weChat.run()
