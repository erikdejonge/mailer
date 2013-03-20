# coding=utf-8
"""

Robust python mailing module, has had a lot of miles in the real world

This source code is licensed under the GNU General Public License,
Version 3. http://www.gnu.org/licenses/gpl-3.0.en.html

Copyright (C)

Erik de Jonge <erik@a8.nl>
Actve8 BV
Rotterdam
www.a8.nl

"""

import smtplib
import os
import re
import mimetypes
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import utils, encoders
from BeautifulSoup import UnicodeDammit

def determine_encoding(text):
    """ tries for charsets \"US-ASCII\", \"ISO-8859-1\", \"UTF-8\"
    @param text:
    """

    possible_charsets = ["US-ASCII", "ISO-8859-1", "UTF-8"]
    for charset in possible_charsets:
        try:
            text.encode(charset)
        except UnicodeError:
            pass
        else:
            return charset
    error_msg = "Unable to determine the correct encoding. Please ensure that a encoding into one of %s is possible." % (
        possible_charsets, )
    raise Exception(error_msg)


#noinspection PyArgumentEqualDefault,PyUnresolvedReferences
def create_message_container(em_from, em_to, em_reply_to):
    """ genereates the dictionary with all the relevant headers
    @param em_from:
    @param em_to:
    @param em_reply_to:
    """

    from_hdr = (utils.formataddr((em_from.name, em_from.email)) if len(em_from.name) > 0 else utils.formataddr(
        (False, em_from.email)))
    reply_to_hdr = (
        utils.formataddr((em_reply_to.name, em_reply_to.email)) if len(em_reply_to.name) > 0 else utils.formataddr(
            (False, em_reply_to.name)))
    to_hdr = (
        utils.formataddr((em_to.name, em_to.email)) if len(em_to.name) > 0 else utils.formataddr((False, em_to.name)))
    from_hdr_charset = determine_encoding(from_hdr)
    reply_to_hdr_charset = determine_encoding(reply_to_hdr)
    to_hdr_charset = determine_encoding(to_hdr)

    # Create message container - This one will house the 'multipart alternative part'
    # and the 'attachments part'.

    mime_mulitpart_mixed = MIMEMultipart("mixed")
    mime_mulitpart_mixed["From"] = Header(from_hdr.encode(from_hdr_charset), from_hdr_charset)
    mime_mulitpart_mixed["To"] = Header(to_hdr.encode(to_hdr_charset), to_hdr_charset)
    mime_mulitpart_mixed["Date"] = Header(utils.formatdate())
    mime_mulitpart_mixed["Reply-To"] = Header(reply_to_hdr.encode(reply_to_hdr_charset), reply_to_hdr_charset)
    mime_mulitpart_mixed["Precedence"] = Header("junk", "US-ASCII")
    mime_mulitpart_mixed["Auto-Submitted"] = Header("auto-generated", "US-ASCII")
    return mime_mulitpart_mixed


#noinspection PyArgumentEqualDefault,PyUnresolvedReferences
def create_mime_multipart_msg(plain_body, html_body):
    """ adds html and text together in one message
    @param plain_body:
    @param html_body:
    """

    html_body_charset = determine_encoding(html_body)
    plain_body_charset = determine_encoding(plain_body)

    # Create message container - the correct MIME type is multipart/alternative.
    # This will house the HTML and Plain Text body

    mime_multipart_msg = MIMEMultipart("alternative")

    # Record the MIME types of both parts - text/plain and text/html.

    part1 = MIMEText(plain_body.encode(plain_body_charset), "plain", plain_body_charset)
    part2 = MIMEText(html_body.encode(html_body_charset), "html", html_body_charset)

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.

    mime_multipart_msg.attach(part1)
    mime_multipart_msg.attach(part2)
    return mime_multipart_msg


def add_attachments(mime_mulitpart_mixed, attachments):
    """ takes list of filenames and adds the mimemessages to the mulipart object
    @param mime_mulitpart_mixed:
    @param attachments:
    """

    for file_name in attachments:
        if not os.path.isfile(file_name):
            continue
        (ctype, encoding) = mimetypes.guess_type(file_name)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.

            ctype = "application/octet-stream"
        (maintype, subtype) = ctype.split("/", 1)
        if maintype == "text":
            file_pointer = open(file_name)
            content = UnicodeDammit(file_pointer.read())
            content_charset = determine_encoding(content.unicode)
            content = content.unicode.encode(content_charset)
            parta = MIMEText(content, _subtype=subtype, _charset=content_charset)
            file_pointer.close()
        elif maintype == "image":
            file_pointer = open(file_name, "rb")
            parta = MIMEImage(file_pointer.read(), _subtype=subtype)
            file_pointer.close()
        elif maintype == "audio":
            file_pointer = open(file_name, "rb")
            parta = MIMEAudio(file_pointer.read(), _subtype=subtype)
            file_pointer.close()
        else:
            file_pointer = open(file_name, "rb")
            parta = MIMEBase(maintype, subtype)
            #noinspection PyUnresolvedReferences
            parta.set_payload(file_pointer.read())
            file_pointer.close()

            # Encode the payload using Base64

            encoders.encode_base64(parta)

        # Set the filename parameter

        #noinspection PyUnresolvedReferences
        parta.add_header("Content-Disposition", "attachment; filename=%s" % os.path.basename(file_name))
        mime_mulitpart_mixed.attach(parta)
    return mime_mulitpart_mixed


def send_message(from_email, to_list, mime_multipart_mixed_message, settings=None):
    """ sends the multipart to the to_list, from email must be an email on the smtp server
    @param from_email:
    @param to_list:
    @param mime_multipart_mixed_message:
    @param settings:
    """

    if not settings:
        raise Exception("no settings object provided")

    mta = smtplib.SMTP(settings.email_host)
    mta.login(settings.email_host_user, settings.email_host_password)
    msg = mime_multipart_mixed_message.as_string()
    result = mta.sendmail(from_email.as_string(), to_list, msg)
    mta.quit()
    return result


def gen_mime_message(header, body, attachments):
    """ builds message
    @param header:
    @param body:
    @param attachments:
    """

    from_hdr = header.from_obj
    to_hdr = header.to_obj
    reply_hdr = header.reply_obj
    subject = header.get_subject()

    # create the mimeobject with the headers, and recipients

    message_container = create_message_container(from_hdr, to_hdr, reply_hdr)

    # create mimeobject with the html and plain text

    plain_body = body.txt
    html_body = body.html
    mime_multipart_msg = create_mime_multipart_msg(plain_body, html_body)

    # attache the message (with html and plain text) to the message container

    #noinspection PyUnresolvedReferences
    message_container.attach(mime_multipart_msg)

    # add the attachments

    message_container = add_attachments(message_container, attachments)

    # set the subject

    subject_charset = determine_encoding(subject)
    message_container["Subject"] = Header(subject.encode(subject_charset), subject_charset)

    return message_container


def GenerateMessage(

        from_name,
        from_email,
        reply_to_name,
        reply_to_email,
        to_name,
        to_email,
        subject,
        html_body,
        plain_body,
        attachments,
):
    """ builds message
    @param from_name:
    @param from_email:
    @param reply_to_name:
    @param reply_to_email:
    @param to_name:
    @param to_email:
    @param subject:
    @param html_body:
    @param plain_body:
    @param attachments:
    """

    from_hdr = EmailName(from_email, from_name)
    to_hdr = EmailName(to_email, to_name)
    reply_hdr = EmailName(reply_to_email, reply_to_name)

    # create the mimeobject with the headers, and recipients

    message_container = create_message_container(from_hdr, to_hdr, reply_hdr)

    # create mimeobject with the html and plain text

    mime_multipart_msg = create_mime_multipart_msg(plain_body, html_body)

    # attache the message (with html and plain text) to the message container

    #noinspection PyUnresolvedReferences
    message_container.attach(mime_multipart_msg)

    # add the attachments

    message_container = add_attachments(message_container, attachments)

    # set the subject

    subject_charset = determine_encoding(subject)
    message_container["Subject"] = Header(subject.encode(subject_charset), subject_charset)

    return message_container


def SendMessage(from_email, to_list, msg):
    """ old style wrapper
    @param from_email:
    @param to_list:
    @param msg:
    """

    return send_message(from_email, to_list, msg)


class EmailName(object):
    """ email, name holder, initialize with email first """

    name = None
    email = None

    def __repr__(self):
        return self.name + " <" + self.email + ">"

    def as_string(self):
        return self.name + " <" + self.email + ">"

    def __init__(self, email, name=None):
        email_pattern =\
        re.compile(
            "(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*|^\"([\\001-\\010\\013\\014\\016-\\037!#-\\[\\]-\\177]|\\\\                       "
            "[\\001-011\\013\\014\\016-\\177])*\")@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\\.)+[A-Z]{2,6}\\.?$",
            re.IGNORECASE)  # dot-atom

        # quoted-string

        if not email_pattern.match(email):
            raise Exception("This is not a valid email address -> " + str(email))
        if not name:
            self.name = email
        else:
            self.name = name
        self.email = email


class EmailHeader(object):
    """ mail header, subject, from, to, reply """

    def __init__(self, subject, from_obj, to_obj, reply_obj):
        self._subject = subject
        self._from_obj = from_obj
        self._to_obj = to_obj
        self._reply_obj = reply_obj

    def set_subject(self, value):
        """ mail subject
        @param value:
        """

        self._subject = value

    def get_subject(self):
        """ mail subject """

        if not self._subject:
            return ""
        return self._subject

    subject = property(get_subject, set_subject)

    def get_from_obj(self):
        """ mail to """

        if not self._from_obj:
            raise Exception("from_obj is not set")
        return self._from_obj

    from_obj = property(get_from_obj)

    def get_to_obj(self):
        """ mail to """

        if not self._to_obj:
            raise Exception("to_obj is not set")
        return self._to_obj

    to_obj = property(get_to_obj)

    def get_reply_obj(self):
        """ mail reply """

        if not self._reply_obj:
            raise Exception("reply_obj is not set")
        return self._reply_obj

    reply_obj = property(get_reply_obj)


class Body(object):
    """ mail body, html and text """

    _txt = None
    _html = None

    def __init__(self, html, txt=None):
        self.html = html
        self.txt = txt

    def set_txt(self, value):
        """ mail message in text
        @param value:
        """

        self._txt = value

    def get_txt(self):
        """ mail message in text """

        if not self._txt:
            #noinspection PyUnusedLocal
            try:
                #noinspection PyUnresolvedReferences
                import html2text

                return str(html2text.html2text(self.html))
            except ImportError, ex:
                return self.html

        return self._txt

    txt = property(get_txt, set_txt)

    def set_html(self, value):
        """ mail message in html
        @param value:
        """

        self._html = value

    def get_html(self):
        """ mail message in html """

        return self._html

    html = property(get_html, set_html)


#noinspection PyArgumentEqualDefault
class Email(object):
    """ object to send an email """

    def __init__(self, settings):
        self.settings = settings
        self._attachments = []
        self._body = None
        self._to_email = None
        self._reply_email = None
        self._subject = None

    def set_subject(self, value):
        """ mail subject
        @param value:
        """

        self._subject = value

    def get_subject(self):
        """ mail subject """

        if not self._subject:
            raise Exception("subject has not been set")
        return self._subject

    subject = property(get_subject, set_subject)

    def set_body(self, value):
        """ Body class
        @param value:
        """

        if type(value) != Body:
            raise Exception("body has to be of type Body")
        self._body = value

    def get_body(self):
        """ Body class """

        if not self._body:
            raise Exception("body has not been set")
        return self._body

    body = property(get_body, set_body)

    def set_to_email(self, email):
        """ EmailName class
        @param email:
        """

        self._to_email = []
        if type(email) == type(tuple()):
            value = EmailName(email[0], email[1])
        else:
            value = EmailName(email, email)
        self._to_email.append(value)

    def get_to_email(self):
        """ EmailName class """

        if self._to_email:
            return self._to_email[0]
        raise Exception("to_email is not set")

    to_email = property(get_to_email, set_to_email)

    def set_extra_address(self, email):
        """ EmailName class
        @param email:
        """

        if type(email) == type(list()):
            emails = email
            for email in emails:
                value = EmailName(email, email)
                self._to_email.append(value)
            return
        else:
            value = EmailName(email, email)
        self._to_email.append(value)

    extra_address = property(None, set_extra_address)

    def set_reply_email(self, email):
        """ EmailName class
        @param email:
        """

        if type(email) == type(tuple()):
            value = EmailName(email[0], email[1])
        else:
            value = EmailName(email, email)
        self._reply_email = value

    def get_reply_email(self):
        """ EmailName class """

        return self._reply_email

    reply_email = property(get_reply_email, set_reply_email)

    def set_attachments(self, value):
        """ add a filename
        @param value:
        """
        if type(value) != type([]):
            raise Exception("must be a list of files")
        self._attachments = value

    def get_attachments(self):
        """ list of filenames """

        return self._attachments

    attachments = property(get_attachments, set_attachments)

    def add_attachment(self, fname):
        """ add a filename to the attachment list
        @param fname:
        """

        self._attachments.append(fname)

    def get_recipient_list(self):
        """ list of emails """

        email_list = [x.email for x in self._to_email]
        return list(set(email_list))

    def send(self):
        """ send the mail """

        if not self.to_email:
            raise Exception("The to_email property has not been set")

        from_obj = EmailName(self.settings.email_from_email, self.settings.email_from)

        if not self.reply_email:
            self.reply_email = (self.settings.email_from_email, self.settings.email_from)
        else:
            from_obj = EmailName(self.settings.email_from_email, self._reply_email.name)

        header = EmailHeader(self._subject, from_obj, self.to_email, self.reply_email)

        message = gen_mime_message(header, self.body, self.attachments)

        return send_message(from_obj, self.get_recipient_list(), message, settings=self.settings)
