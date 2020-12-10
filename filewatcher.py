# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 10:47:28 2020

@author: markb
"""
import os
import sys
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

import boto3
from botocore.exceptions import ClientError

def onCreated(event):
    print(f"{event.src_path} created")
    sendEmail("{0} created".format(event.src_path))

def onDeleted(event):
    print(f"{event.src_path} deleted")
    sendEmail("{0} deleted".format(event.src_path))

def onModified(event):
    print(f"{event.src_path} modified")
    sendEmail("{0} modified".format(event.src_path))

def onMoved(event):
    print(f"{event.src_path} moved to {event.dest_path}") 
    sendEmail("{0} moved to {1}".format(event.src_path, event.dest_path))
    
def sendEmail(message):
    FROM = "Sender Name <noreply@solutionsitw.com>"
    
    TO = "mbixler@solutionsitw.com"
    
    AWS_REGION = "us-east-1"
    
    SUBJECT = "Filewatcher email"
    
    BODY_TEXT = message
    
    BODY_HTML = """<html>
    <head></head>
    <body>
        <h1>Filewatcher Alert</h1>
        <p>{0}</p>
    </body>
    </html>
    
    """
    
    BODY_HTML = BODY_HTML.format(message)
    
    CHARSET = "UTF-8"
    
    client = boto3.client("ses", region_name=AWS_REGION)
    
    try:
        response = client.send_email(
                Destination={
                        'ToAddresses': [
                                TO
                        ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': BODY_HTML,
                        },
                        'Text': {
                            'Charset': CHARSET,
                            'Data': BODY_TEXT,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': SUBJECT,
                    }
                },
                Source=FROM
            )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent. Message ID: {0}".format(response['MessageId']))
    

if __name__ == "__main__":
    # Set up pidfile
    pid = os.getpid()
    pidfile = os.path.join(str(Path.home()), ".filewatcher", "process.pid")
    with open(pidfile, "w") as pidfile:
        pidfile.write(str(pid))
    
    patterns = '*'
    ignorePatterns = ''
    ignoreDirectories = False
    caseSensitive = True
    eventHandler = PatternMatchingEventHandler(patterns, ignorePatterns, ignoreDirectories, caseSensitive)
    # Set up events
    eventHandler.on_created = onCreated
    eventHandler.on_deleted = onDeleted
    eventHandler.on_modified = onModified
    eventHandler.on_moved = onMoved
    
    path = sys.argv[1] if len(sys.argv) > 1 else '.' 
    recursive = True
    observer = Observer()
    observer.schedule(eventHandler, path, recursive=recursive)
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        
    
