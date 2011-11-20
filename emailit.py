#!/usr/bin/env python3
from argparse import ArgumentParser, FileType
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import argparse
import os
import subprocess
import sys

import markdown

def resolve_path(origin_path, relative_path):
    return os.path.join(os.path.dirname(origin_path), relative_path)

with open(resolve_path(__file__, 'template.html')) as template_file:
    TEMPLATE = template_file.read()

TEMPLATE_FACEBOOK_EVENT = ''' | <a
href="http://www.facebook.com/event.php?eid={event_id}" target="_blank"
style="color: #336699; font-weight: normal; text-decoration:
underline;">Facebook event</a> '''

TEMPLATE_IMAGE = '''<img src="http://man-up.appspot.com/img/{image_name}"
style="max-width: 560px; border: none; font-size: 14px; font-weight: bold;
height: auto; line-height: 100%; outline: none; text-decoration: none;
text-transform: capitalize; display: inline;">'''

def make_email(from_, subject, body, facebook_event, image_name,
        image_link):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_

    msg.attach(MIMEText(body))

    if facebook_event:
        facebook_event = TEMPLATE_FACEBOOK_EVENT.format(
            event_id=facebook_event)
    else:
        facebook_event = ''

    if image_name:
        image = TEMPLATE_IMAGE.format(image_name=image_name)
        if image_link:
            image = '<a href="%s" target="_blank">%s</a>' % (image_link, image)
    else:
        image = ''


    html = TEMPLATE.format(
        body=markdown.markdown(body),
        image=image,
        facebook_event=facebook_event)

    msg.attach(MIMEText(html, 'html'))

    return msg

def build_argument_parser():
    argument_parser = argparse.ArgumentParser(
        fromfile_prefix_chars='@', description=
        'EmailIT automatically produces and sends emails, using a supplied '
        'body text, subject, and receipient list.', prog='EmailIT')

    argument_parser.add_argument('to', nargs='+',
        help='Email receipients. For a file of receipients, use @address_file.')

    argument_parser.add_argument('frm',
        help='The source email address for the email.')

    argument_parser.add_argument('subject',
        help='The subject of the e-mail.')

    argument_parser.add_argument('body', type=FileType('r'),
        help='A text file containing the desired body of the event email.')

    argument_parser.add_argument('-d', '--dry-run', action='store_true',
        help="Don't actually send any e-mails.")

    argument_parser.add_argument('-f', '--facebook-event', type=int,
        help='The Facebook event ID of the meeting event.')

    argument_parser.add_argument('-i', '--image-name',
        help='The location of the image file to display.')

    argument_parser.add_argument('-l', '--image-link',
        help='A URL for the image file, which will be presented as a hyperlink '
             '(requires --image-name).')

    return argument_parser

def main(argv=None):
    if argv is None:
        argv = sys.argv
    argument_parser = build_argument_parser()
    arguments = argument_parser.parse_args(args=argv[1:])

    with arguments.body as body_file, open(os.devnull, 'w') as devnull:
        body = body_file.read()
        for to in arguments.to:
            print('%s...' % to, end='')
            msg = make_email(arguments.frm, arguments.subject, body,
                arguments.facebook_event, arguments.image_name,
                arguments.image_link)
            msg['To'] = to
            msg_str = msg.as_string()
            if not arguments.dry_run:
                sendmail = subprocess.Popen(('/usr/sbin/sendmail', '-v', to),
                    stdin=subprocess.PIPE, stdout=devnull)
                sendmail.communicate(msg_str.encode('ascii'))
                print('done')
            else:
                print('skipped')

    return 0

if __name__ == '__main__':
    exit(main())

