# coding=utf-8

"""
CouchDB library to save python objects, handles conflict resolution on class attribute level.

Erik de Jonge
Actve8 BV
Rotterdam

erik@a8.nl
www.a8.nl

"""

from __init__ import Email, Body


#noinspection PyUnusedLocal
class Setting(object):
    """ settings object, with config info, can also be a django settings object """

    email_host = "smtp.gmail.com:587"
    email_host_password = "kjhfsd98"
    email_host_user = "cryptobox.node.errors@gmail.com"
    email_from_email = "cryptobox.node.errors@gmail.com"
    email_from = "test email mailer"


def main():
    """ test mailer """

    settings = Setting()
    email = Email(settings)
    email.reply_email = ("erik@a8.nl", "Erik de Jonge")
    email.to_email = ("erik@a8.nl", "Erik de Jonge Reply")
    email.subject = "Hello world subject?"
    email.add_attachment("README.md")
    email.body = Body("<html><head><title>hello</title></head><body><b>hello world</b><br/><i>en dit is italic</i></body></html>")
    email.send()

    settings.email_host = "mail.active8.nl"
    settings.email_host_password = "48fi0b"
    settings.email_host_user = "erik@active8.nl"

    email = Email(settings)
    email.reply_email = ("erik@a8.nl", "Erik de Jonge")
    email.to_email = ("erik@a8.nl", "Erik de Jonge Reply")
    email.subject = "Hello world subject?"
    email.add_attachment("README.md")
    email.body = Body("<html><head><title>hello</title></head><body><b>hello world</b><br/><i>en dit is italic</i></body></html>")
    #email.send()

if __name__ == "__main__":
    main()
