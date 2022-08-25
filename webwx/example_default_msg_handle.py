import webwx


if __name__ == '__main__':
    weChat = webwx.webwx()
    weChat.login()
    weChat.run()
