# ICPC报名信息核对

在有excel报名表的情况下，与icpc.global信息进行核对。

## 准备数据

1. 新建config.yaml，内容：

```yaml
email:
  sender_email: xx@xx.xx
  password: xxxxxx
  smtp_server: xxx
  smtp_port: xxx
  reply_to: xxxx

network:
  http_proxy: xxx
  https_proxy: xxx
```

2. 新建一个token.txt,填入icpc.global中具有管理权限的token，保存到data文件夹。

3. 修改data/constant.py中的变量，根据变量名就能知道什么意思，需要注意的是，前面的一些变量修改后就不用动了，后面有一些要根据需要每次运行前修改。

## 运行

修改main.py中的check_id。相同check_id的情况下，不会对同一个人重复发送电子邮件。例如，运行过程中程序挂掉了，此时只要不改check_id,重新运行不会给之前信息有误的且发送过邮件的队伍再次发送。
如果改了check_id，则在遇到信息有误的队伍会重新发送邮件。

