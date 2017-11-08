# -*- coding: utf-8 -*-
import json
import os
import smtplib
from email.MIMEText import MIMEText
from email import Utils
from time import sleep
from threading import Thread
import logging


EMAIL_FILE = 'emails.json'
PENDING_EMAIL_FILE = 'emails_pending.json'
logger = logging.getLogger('email_sender')


def main():
    # set up logging to file
    format_string = '%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format_string)
    logging.basicConfig(level=logging.DEBUG,
                        format=format_string,
                        filename='email-sender.log',
                        filemode='a')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    logger.info('Starting email sender')

    info = {'stop': False}
    thread = Thread(target=worker, args=(info,))
    thread.start()
    while True:
        try:
            sleep(5)
        except KeyboardInterrupt:
            info['stop'] = True
            logger.info('Terminating email sender')
            break
    thread.join()


def worker(arg):
    while not arg['stop']:
        try:
            logger.info('Collect emails')
            if not os.path.isfile(PENDING_EMAIL_FILE):
                if os.path.isfile(EMAIL_FILE):
                    # Rename file to indicate emails are read to send
                    os.rename(EMAIL_FILE, PENDING_EMAIL_FILE)
                else:
                    logger.info('There are no emails to send')
                    sleep(5)
                    continue
        except:
            logger.error("failed to check for email file")


        # Read email JSON file
        with open(PENDING_EMAIL_FILE) as data_file:
            data = json.load(data_file)

        emails = data['emails']
        server = smtplib.SMTP("smtp.gmail.com", 587)

        # establish connection to smtp server
        try:
            connect_to_server(server)
            logger.info("successfully logged in")
        except:
            logger.error("failed to connect to server")
            continue

        # send email
        # TODO: send email and delete JSON file
        for email in emails:
            send_email(server, email['to'], email['subject'].encode('utf-8'), email['body'].encode('utf-8'))
            try:
                logger.info("successfully sent the mail")
            except:
                logger.error("failed to send mail", email)

        os.remove(PENDING_EMAIL_FILE)

        # close connection to server
        try:
            server.close()
            logger.info("closed connection to server")
        except:
            logger.error("failed to close connection")


def connect_to_server(server):
    gmail_user = 'typeinpw.study@gmail.com'
    gmail_pwd = '' # your password

    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_pwd)


def send_email(server, to, subject, body):
    from_email = 'Studie zur Passworteingabe <typeinpw.study@gmail.com>'

    # Prepare actual message
    msg = MIMEText(body)
    msg['To']       = to
    msg['From']     = from_email
    msg['Subject']  = subject
    msg['Date']     = Utils.formatdate(localtime = True)
    msg['Message-ID'] = Utils.make_msgid()

    # message = "From: {}\nTo: {}\nSubject: {}\n\n{}".format(from_email, to, subject, body)

    server.sendmail(msg['From'], [msg['To']], msg.as_string())


if __name__ == '__main__':
    main()
