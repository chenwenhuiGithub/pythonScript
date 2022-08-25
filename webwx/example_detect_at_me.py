import webwx


def msg_handle(self, msg):
    if msg['senderType'] == 'GROUP' and msg['msgType'] == 'TEXT' and msg['isAtMe'] == True:
        if msg['userDisplayName']:
            print(msg['groupNickName'] + ' - ' + msg['userDisplayName'] + u' - @我')
        else:
            print(msg['groupNickName'] + ' - ' + msg['userNickName'] + u' - @我')
        print('    ' + msg['content'])


if __name__ == '__main__':
    weChat = webwx.webwx()
    weChat.register_msg_handle(msg_handle)
    weChat.login()
    weChat.run()
