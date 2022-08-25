import webwx


def msg_handle(self, msg):
    if msg['msgType'] in ["IMAGE", "VOICE", "VIDEO", "FILE"]:
        msg['downloadFunc'](msg)


if __name__ == '__main__':
    weChat = webwx.webwx()
    weChat.register_msg_handle(msg_handle)
    weChat.login()
    weChat.run()
