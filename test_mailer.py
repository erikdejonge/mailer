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



def main():
    """ test mailer """


    email = Email()
    email.reply_email = ("info@cryptobox.nl", "Cryptobox")
    email.to_email = ("cryptobox.info@gmail.com", "Erik de Jonge Reply")
    email.subject = "Hello world subject?"
    #email.add_attachment("README.md")
    email.body = Body("<html><head><title>hello</title></head><body><b>hello world</b><br/><i>en dit is italic</i></body></html>")
    email.send()

if __name__ == "__main__":
    main()
