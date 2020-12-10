# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 10:46:24 2020

@author: markb
"""

import psutil
import os
from pathlib import Path
import sys
import subprocess

def getWatchFile():
    return os.path.join(str(Path.home()), ".filewatcher", "filewatcher.config")

def getPidfile():
    return os.path.join(str(Path.home()), ".filewatcher", "process.pid")

def getPid():
    pidfile = getPidfile()
    if os.path.exists(pidfile):
        pid = 0
        with open(pidfile) as file:
            pid = file.read()
        if(pid != 0):
            try:
                return psutil.Process(int(pid))
            except:
                return None
        else:
            return None
    else:
        return None
    
def getWatchDir():
    configFile = getWatchFile()
    watchDir = "."
    try:
        with open(configFile) as file:
            watchDir = file.read()
        return watchDir
    except:
        return watchDir

def setWatchDir(watchDir):
    pid = getPid()
    if pid is not None:
        print("Cannot set watch dir while watchdog is running")
        return
    
    configFile = getWatchFile()
    with open(configFile, "w") as file:
        file.write(watchDir)

def checkStatus():
    pid = getPid()
    if pid is not None:
        print(pid.status)
    else:
        print("Not Running")
        
def startProcess():
    pid = getPid()
    if pid is None:
        if len(sys.argv) > 2:
            setWatchDir(sys.argv[2])
             
        watchPath = getWatchDir()
        print("starting watchdog")
        with open("watchdog_log.log", "a") as logfile:
            # subprocess.Popen(["python3", "filewatcher.py", watchPath]) #, stdout=logfile, stderr=logfile)
            filename = "filewatcher.exe" if sys.platform == "win32" else "filewatcher"
            watcherPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "bin", filename)
            subprocess.Popen([watcherPath, watchPath])
    else:
        print("watchdog is already running")
    
def stopProcess():
    pid = getPid()
    if pid is not None:
        print("stopping watchdog")
        pid.kill()
    else:
        print("watchdog is not running")

if __name__ == "__main__":   
    configFolder = os.path.join(str(Path.home()), ".filewatcher")
    if not os.path.exists(configFolder):
        os.mkdir(configFolder)
    if len(sys.argv) > 1:
        if sys.argv[1] == "start":
            # start watchdog process
            startProcess()
        elif sys.argv[1] == "stop":
            # stop the watchdog process
            stopProcess()
        elif sys.argv[1] == "status":
            checkStatus()
        elif sys.argv[1] == "set-dir":
            if len(sys.argv) < 3:
                print("Please specify watch dir")
            else:
                setWatchDir(sys.argv[2])
        elif sys.argv[1] == "get-dir":
            dir = getWatchDir()
            print(dir)
        else:
            print("unknown command: {0}".format(sys.argv[1]))