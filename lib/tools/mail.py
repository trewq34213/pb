import smtplib
import multiprocessing
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.header import Header


# 异步发邮件
def sendmail(receiver, subject, content, img=False):
    p = multiprocessing.Process(target=inner_sendmail, args=(receiver, subject, content, img,))
    p.start()


# 发邮件(可指定附件图片)
def inner_sendmail(receiver, subject, content, img=False):
    host = "your host"
    sender = 'your email'
    password = "your password"

    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    message = MIMEMultipart()
    message['Subject'] = Header(subject, 'utf-8')
    message['From'] = Header("涛哥", 'utf-8')  # 发送者
    message['To'] = Header(receiver, 'utf-8')  # 接收者
    message.attach(MIMEText(content, 'plain', 'utf-8'))  # 正文
    if img != False:
        file = open(img, mode='rb')
        attachment = MIMEImage(file.read(), _subtype='octet-stream')
        attachment.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', img))
        message.attach(attachment)

    try:
        smtpObj = smtplib.SMTP_SSL(host, 465)
        smtpObj.login(sender, password)
        smtpObj.sendmail(sender, receiver, message.as_string())
        return True
    except smtplib.SMTPException as e:
        hander = open("tmp/logs/sendmail_exception.log", 'a+')
        print(subject + ":" + content + ":" + str(e), file=hander)
        hander.close()
        return False
