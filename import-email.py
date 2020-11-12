import imaplib
import sys
import email
import datetime
import logging
import os

mailserver = os.environ.get('MAIL_SERVER', 'localhost')
login = os.environ.get('MAIL_USER', None)
password = os.environ.get('MAIL_PASSWD', None)
dest_dir = 'data'

logging.basicConfig(level=logging.INFO, format='%(asctime)s|%(levelname)s|%(message)s')

# save payload of text message
def save_text_msg(msg):
    timestamp = datetime.datetime.now().strftime('%y%m%d_%H%M%S.%f')
    filename = f'{dest_dir}/payload_{timestamp}.txt'
    with open(filename, 'wb') as f:
        f.write(msg.get_payload(decode=True))

# connect to the mailserver using imap4 ssl protocol
mb = imaplib.IMAP4_SSL(host=mailserver)
mb.login(login, password)

# select the INBOX directory
mb.select()

# get all UNFLAGGED message ids
status, data = mb.search(None, 'UNFLAGGED')
if status != 'OK':
    logging.error('IMAP search status not ok')
    sys.exit(1)
msgids = data[0].split()

# fetch the messages and set the 'Flagged' flag after processed
logging.info(f'Found {len(msgids)} Unflagged messages')
imported = 0
for msgid in msgids:
    status, data = mb.fetch(msgid, '(RFC822)')
    if status == 'OK':
        msg = email.message_from_bytes(data[0][1])
        # only save simple text message, no multipart
        if not msg.is_multipart() and msg.get_content_maintype() == 'text':
            save_text_msg(msg)
            imported += 1
        mb.store(msgid, '+FLAGS', '\\Flagged')
    else:
        logging.error('IMAP fetch status not ok')
mb.close()
mb.logout()
logging.info(f'Import {imported} text messages')