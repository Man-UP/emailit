#!/usr/bin/env python3
from __future__ import print_function
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

TEMPLATE_FACEBOOK_EVENT = '''
 | <a href="http://www.facebook.com/event.php?eid={event_id}" target="_blank" style="color: #336699; font-weight: normal; text-decoration: underline;">Facebook event</a>
'''

TEMPLATE_IMAGE = '''
<img src="http://man-up.appspot.com/img/{image_name}" style="max-width: 560px; border: none; font-size: 14px; font-weight: bold; height: auto; line-height: 100%; outline: none; text-decoration: none; text-transform: capitalize; display: inline;">
'''

TEMPLATE_ONLINE_VERSION = '''
<td valign="top" width="190">
    <div style="color: #505050; font-family: Arial; font-size: 10px; line-height: 100%; text-align: left;">
        Not displaying correctly?<br>
        <a href="http://man-up.appspot.com/messages/{index}" target="_blank"   style="color: #336699; font-weight: normal; text-decoration: underline;">View browser</a>.
    </div>
</td>
'''

def make_email(from_, subject, body_path, facebook_event, image_name,
        image_link, online_index):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_

    #with open(body_path) as body_file:
    body_plain = body_path.read()

    msg.attach(MIMEText(body_plain))

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


    if online_index is not None:
        online_version = TEMPLATE_ONLINE_VERSION.format(
            index=online_index)
    else:
        online_version = ''

    html = TEMPLATE.format(
        body=markdown.markdown(body_plain),
        image=image,
        facebook_event=facebook_event,
        online_version=online_version)

    msg.attach(MIMEText(html, 'html'))

    return msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    ap = argparse.ArgumentParser(fromfile_prefix_chars='@')
    ap.add_argument('-b', '--body', required=True, type=argparse.FileType('r'), help='A text file containing the desired body of the event email.')
    ap.add_argument('-d', '--dry-run', action='store_true', help='A flag to indicate that no action should be taken (TODO: Write the email etc. to a file?)')
    ap.add_argument('-f', '--from', dest='from_', required=True, type=str, help='The source email address for the email.')
    ap.add_argument('-F', '--facebook-event', type=int, help='A facebook event ID for the meeting (i.e. the number after "sk=group_" in the URL')
    ap.add_argument('-i', '--image-name', type=str, help='The location of the image file to display')
    ap.add_argument('-l', '--image-link', type=str, help='A URL for the image file, which will be presented as a hyperlink (requires --image-name)')
    ap.add_argument('-o', '--online-index', type=int, help='The index on the Man-UP website for this event (e.g. http://man-up.appspot.com/messages/<online_index>)')
    ap.add_argument('-s', '--subject', required=True, type=str, help='Email Subject')
    ap.add_argument('-t', '--to', nargs='+', required=True, type=str, help='Email receipients as a list (e.g. `cat addresses`... TODO: Is this the way to send to multiple receipients? :S)')
    args = ap.parse_args(args=argv[1:])



    with open(os.devnull, 'w') as devnull:
        for to in args.to:
            print('%s...' % to, end='')
            msg = make_email(args.from_, args.subject, args.body,
                args.facebook_event, args.image_name, args.image_link,
                args.online_index)
            msg['To'] = to
            msg_str = msg.as_string()
            if not args.dry_run:
                sendmail = subprocess.Popen(('/usr/sbin/sendmail', '-v', to),
                    stdin=subprocess.PIPE, stdout=devnull)
                sendmail.communicate(msg_str.encode('ascii'))
                print('done')
            else:
                print('skipped')
    args.body.close()

    return 0

if __name__ == '__main__':
    exit(main())

