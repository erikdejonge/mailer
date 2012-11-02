# pylint: disable-msg=C0103
# pylint: enable-msg=C0103
# tempfile regex format
#
# pylint: disable-msg=C0111
# missing docstring
#
# pylint: disable-msg=W0232
# no __init__ method
#
# pylint: disable-msg=R0903
# to few public methods
#
# DISABLED_ylint: disable-msg=R0201
# method could be a function
#
#!/usr/bin/python
# -*- coding: utf-8 -*-

# pylint: disable-msg=C0103
# pylint: enable-msg=C0103
# tempfile regex format, surpress komodo's pylint implementation


"""
CouchDB library to save python objects, handles conflict resolution on class attribute level.

Erik de Jonge
Actve8 BV
Rotterdam

erik@a8.nl
www.a8.nl

"""

from __init__ import Email, Body


class Setting(object):
    """ settings object, with config info, can also be a django settings object """

    email_host = "mail.server.com"
    email_host_password = "password"
    email_host_user = "smtp_user_name"
    email_from_email = "email@somehost.com"
    email_from = "test email mailer"

    def randommethod(self):
        """ method to silence pylint """

        self = self

    def randommethod1(self):
        """ method to silence pylint """

        self = self


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


if __name__ == "__main__":
    main()
