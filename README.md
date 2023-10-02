# ICPC报名信息核对

在有excel报名表的情况下，与icpc.global信息进行核对。

## 准备数据

1. 新建config.ini，内容：

```ini
[Email]
sender_email = 123456@qq.com
password =  xxx
smtp_server = smtp.xx.com
smtp_port = xxx
```

2. 新建一个token.txt,填入icpc.global中具有管理权限的token

3. 修改constant.py中的变量，根据变量名就能知道什么意思，需要注意的是，前面的一些变量修改后就不用动了，后面有一些要根据需要每次运行前修改。

## 运行

修改main.py中的check_id。相同check_id的情况下，不会对同一个人重复发送电子邮件。