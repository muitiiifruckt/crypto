import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

PASSWORD = "pass"
def sendEmail(subject, body, to_email, from_email):
    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
    smtp_server.starttls()
    smtp_server.login(from_email, PASSWORD)

    msg = MIMEMultipart()
    # Настройка параметров сообщения
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg["Body"] = body


    # Отправка письма
    smtp_server.sendmail(from_email, to_email, msg.as_string())

    # Закрытие соединения
    smtp_server.quit()
