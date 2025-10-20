import os.path
import smtplib
import ssl
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml  # Import the yaml module
import re

from utils.icpcglobal import logger
from utils.logger import setup_logger
# Load the YAML configuration file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Access configuration data
sender_email = config['email']['sender_email']
password = config['email']['password']
reply_to = config['email']['reply_to']
# Other email sending code...
logger = setup_logger()


class Mail:
    def __init__(self):
        self.server = None
        self.sender_email = config['email']['sender_email']
        self.password = config['email']['password']
        self.smtp_server = config['email']['smtp_server']
        self.smtp_port = config['email']['smtp_port']
        self.context = ssl.create_default_context()
        self.login()

    def login(self):
        self.server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=self.context)
        self.server.login(self.sender_email, self.password)

    def send(self, receiver:str, title, body):
        reg = r"^[A-Za-z0-9]+([_\.][A-Za-z0-9]+)*@([A-Za-z0-9\-]+\.)+[A-Za-z]{2,6}$"
        if re.match(reg, receiver) is None:
            logger.error(f"Invalid email address: {receiver}")
            return
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = receiver
        message["Subject"] = title
        message["Reply-To"] = reply_to  # 设置回复邮箱地址

        message.attach(MIMEText(body, "html"))
        self.save_to_file(message,body)
        try:
            self.server.sendmail(self.sender_email, receiver, message.as_string())
        except Exception as err:
            logger.error(f"发送邮件失败:{err}")

    def save_to_file(self,message:MIMEMultipart,body):
        name = f"{message['To']}-{message['Subject']}.html"
        path ="email"
        path_name = os.path.join(path, name)
        os.makedirs(path, exist_ok=True)
        with open(path_name,"w",encoding="utf-8") as f:
            f.write(body)

if __name__ == '__main__':
    # Example usage:
    mail_client = Mail()
    mail_client.send("2386360020@qq.com", "Hello", "<h1>Test Email</h1>")
