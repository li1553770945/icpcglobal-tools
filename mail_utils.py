import smtplib
import ssl
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import configparser

# 创建并读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 从配置文件中获取发送者邮箱地址和密码
sender_email = config.get('Email', 'sender_email')
password = config.get('Email', 'password')

# 其他邮件发送代码...


class Mail:
    def __init__(self):
        self.server = None
        self.sender_email = config.get('Email', 'sender_email')
        self.password = config.get('Email', 'password')
        self.smtp_server = config.get('Email', 'smtp_server')
        self.smtp_port = int(config.get('Email','smtp_port'))
        self.context = ssl.create_default_context()
        self.login()

    def login(self):
        self.server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=self.context)
        self.server.login(self.sender_email, self.password)

    def send(self, receiver, title, body):
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = receiver
        message["Subject"] = title

        body = body
        message.attach(MIMEText(body, "html"))

        # print(receiver,title,body)
        self.server.sendmail(self.sender_email, receiver, message.as_string())
        time.sleep(1)
