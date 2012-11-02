mailer
======

Python mail object. Wrapper around smtplib and the email python.
Robust python mailing module, has had a lot of miles in the real world


Usage
=====

Simple but robust emailing from python


```python
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
```
