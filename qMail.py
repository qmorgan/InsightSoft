#!/bin/env python
"""
qMail.py 

qMail.domail('qmorgan@gmail.com','Subject String','Body String\n\nYay',\
         attach_files=['/full/file/path1.jpg','/full/file/path2.txt'],undisclosed=True)
         
Set up your environment variables permanently in e.g. your ~/.bashrc file:
export Q_GMAIL_ACCOUNT='yourUsernameHere'
export Q_GMAIL_PASS='yourPasswordHere'

Note this is NOT a secure way to store username and passwords. Use with 
caution. Best to create a new gmail account that you don't mind security 
issues with.

Adapted from https://github.com/qmorgan/qsoft/tree/master/Software/AutoRedux/send_gmail.py

Modified from Josh Bloom's "domail.py" to send an email from gmail.
amorgan removed vestigial code from when the email was sent via other methods.
"""

import os, sys, string, stat, socket,smtplib

import threading, time, traceback

os.umask(0)
userpath = os.environ.get("HOME")

# Check to make sure the environment variables are set up correctly
if not os.environ.has_key("Q_GMAIL_ACCOUNT"):
    print "You need to set the environment variable Q_GMAIL_ACCOUNT to"
    print "point to your gmail account name"
    sys.exit(1)
else:
    gmail_username = os.environ.get("Q_GMAIL_ACCOUNT")
    

if not os.environ.has_key("Q_GMAIL_PASS"):
    print "You need to set the environment variable Q_GMAIL_PASS to"
    print "point to your gmail password"
    sys.exit(1)
else: 
    gmail_password = os.environ.get("Q_GMAIL_PASS")

undisclosed = False # Suppress recipient list?
from_address = gmail_username+'@gmail.com'

# JSB comments out so we can use gmail
#defhost  = 'localhost'

# use gmail
# see http://gmail.google.com/support/bin/answer.py?answer=13287
defhost  = 'smtp.gmail.com'

# http://mail.python.org/pipermail/python-list/2003-September/225406.html
# http://snippets.dzone.com/posts/show/757
import mimetypes
from email.Encoders import encode_base64
from email.MIMEAudio import MIMEAudio
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText


def usage():
    print "[USAGE] qMail.py 'mailto' 'mailsubject' 'messagebody'"
    return

def getAttachment(path, filename):
     ctype, encoding = mimetypes.guess_type(path)
     if ctype is None or encoding is not None:
         ctype = 'application/octet-stream'
     maintype, subtype = ctype.split('/', 1)
     fp = open(path, 'rb')
     if maintype == 'text':
         attach = MIMEText(fp.read(),_subtype=subtype)
     elif maintype == 'message':
         attach = email.message_from_file(fp)
     elif maintype == 'image':
         attach = MIMEImage(fp.read(),_subtype=subtype)
     elif maintype == 'audio':
         attach = MIMEAudio(fp.read(),_subtype=subtype)
     else:
         print maintype, subtype
         attach = MIMEBase(maintype, subtype)
         attach.set_payload(fp.read())
         encode_base64(attach)
     fp.close
     attach.add_header('Content-Disposition', 'attachment',
			filename=filename)
     return attach

def domail(mailto, mailsub, mailbody, attach_files=[], sig=True, undisclosed=False ,fromaddr = from_address, html=False):

    ## here we want to thread so that we dont block
    t = threading.Timer(0.01,intdomail,args=[mailto,mailsub,mailbody],\
                    kwargs={'attach_files':attach_files,'undisclosed':undisclosed,'fromaddr':fromaddr,'html':html})
    t.start()
    return

def intdomail(mailto, mailsub, mailbody, attach_files=[], sig=True, undisclosed=False, fromaddr = from_address, html=False):

    mailto = mailto.split()
    # print mailto
    badlist = ['cfa','harvard','at','cfa-wide','oir',' ','cfhelp','all',\
               'dot','@','dt','ssp','postdocs','faculty','grad']

    mlist = []
    for addr in mailto:
	#print addr[-3:]
	#print ((addr.lower() not in badlist), (addr.find("@") != -1), \
        #   (addr.find(".") != -1),(addr[-3:] == "edu"))

        if (addr.lower() not in badlist) and (addr.find("@") != -1) and \
           (addr.find(".") != -1):
            mlist.append(addr)

    mailto = mlist
    if len(mailto) == 0:
	print "no valid email"
        return
    
    mailhost = defhost
    
    tolist = ", ".join(mailto)
    if undisclosed == True: 
        tolist = "undisclosed@recipients.com"
    
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = tolist
    msg['Subject'] = mailsub
    if sig:
        mailbody += '\n\n----\nThis message was sent automatically.  If you feel you received this message in error, please contact Adam Morgan at qmorgan@gmail.com'
    
    # attach the text; as either plain or html
    if html == False:
        msg.attach( MIMEText(mailbody,'plain') )
    else:
        msg.attach( MIMEText(mailbody,'html') )
        
    for attachpath in attach_files:
        # Re-write if you want to attach the files with a different file name
        # Right now, just take the actual name of the file.
        attachfilename = attachpath.split('/')[-1]
        attach = getAttachment(attachpath, attachfilename)
        msg.attach(attach)
    

    server = smtplib.SMTP(mailhost,587)

    ttt = server.ehlo()
    # print ttt
    if 1:
        a = server.starttls()
        # print a
    else:
        print 'could not start a secure SSL session for mail'

    b = server.ehlo()
    # print b
    try:
        c = server.login(gmail_username,gmail_password)
        # print c
	# print (fromaddr, mailto, msg)
        d = server.sendmail(fromaddr, mailto, msg.as_string())
        # print d
    except:
        print "send mail failed"
        print traceback.format_exc()

    try:
        del server
    except:
        pass
    return

# Just call main
if __name__ == '__main__':

    if (len(sys.argv) != 4):
        print usage()
        sys.exit(0)
        
    if ((sys.argv[1] == '-h') or (sys.argv[1] == "--h")):
        print usage()
        sys.exit(0)
    
    # Change if want to be able to send attachments from command line    
    domail(sys.argv[1],sys.argv[2],sys.argv[3])
    sys.exit(0)
