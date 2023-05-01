import imaplib
import email
import os
from email.header import decode_header
import telebot
import time


lastTime = ""  # last time of message
chatId = "chat id of desired chat"
bot = telebot.TeleBot("Your Telegram Bot Token")


def checkItem(item):  # проверяем заголовок/ имя фамилию
    try:
        ans = decode_header(item)[0][0].decode('utf-8')
    except AttributeError:
        ans = item
    return ans


def get_inf(email_message):  # получаем текст из email сообщения
    if email_message.is_multipart():
        for k in email_message.walk():
            if isinstance(k.get_payload(), str):
                try:
                    return k.get_payload(decode=True).decode("utf-8")  # текст
                except UnicodeDecodeError:
                    return k.get_payload(decode=True).decode("cp1252")
    for k in email_message.walk():
        return k.get_payload()  # текст


def send_inf(email_message):
    user = email_message['From'].split()
    messageAns = ""
    messageAns += email_message['Date']  # дата
    messageAns += f"\n{checkItem(user[0])} "  # имя фамилия
    try:
        messageAns += user[1]  # почта
    except IndexError:
        pass
    messageAns += f"\n{checkItem(str(email_message['Subject']).strip())}\n\n"  # Заголовок
    messageAns += get_inf(email_message)

    for k in email_message.walk():
        if k.get_filename() and k.get_filename()[-3:] not in ["rar", "zip"]:
            file = k.get_payload(decode=True)
            with open(k.get_filename(), "wb") as writeFile:
                writeFile.write(file)
            if k.get_filename()[-3:] in ["jpg", "jpeg", "png"]:
                bot.send_photo(chatId, open(k.get_filename(), "rb"), timeout=120)
            else:
                bot.send_document(chatId, open(k.get_filename(), "rb"), timeout=120)
            os.remove(k.get_filename())
    if len(messageAns) < 20000:
        bot.send_message(chatId, messageAns, timeout=40)


def parseMail(count):  # parsing of count last messages
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    mail.login('Your Google Email', 'Your password')
    mail.select('INBOX')
    result, data = mail.search(None, "ALL")
    ids = data[0].split()
    for k in range(count, 1, -1):
        latest_email_id = ids[-1*k]
        result1, data1 = mail.fetch(latest_email_id, "(RFC822)")
        send_inf(email.message_from_bytes(data1[0][1]))


def getLast():  # last message
    mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    mail.login('Your Google Email', 'Your password')
    mail.select('INBOX')
    result, data = mail.search(None, "ALL")
    ids = data[0].split()
    latest_email_id = ids[-1]
    result1, data1 = mail.fetch(latest_email_id, "(RFC822)")
    return data1[0][1]


if __name__ == "__main__":
    parseMail(30)
    while True:
        print("New check")
        raw_email = getLast()
        emailMessage = email.message_from_bytes(raw_email)
        if not len(lastTime):
            lastTime = emailMessage['Date']
            send_inf(emailMessage)
        else:
            if lastTime != emailMessage['Date']:
                send_inf(emailMessage)

        time.sleep(100)






