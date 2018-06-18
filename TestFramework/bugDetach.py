#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import os, logging, coloredlogs
# from adbExtend import adbExtend
import threading
import time
import ConfigParser

coloredlogs.install()

class BugDetach(object):

    def __init__(self):
        self.runningFlag = True
        self.section = 'Stability'
        self.loadKeywords()
        self.setLogFile()
        self.logfilePath = 'log'
        if not os.path.exists(self.logfilePath):
            os.mkdir(self.logfilePath)

    def loadKeywords(self, path = './keywords.conf'):
        config = ConfigParser.ConfigParser()
        config.read(path)
        # all = config.get('Stability','CRASH')
        self.keywords = config.items(self.section)

    def showKeywords(self):
        for line in self.keywords:
            print line[0] + ':' + line[1]

    def bugAssert(self, logFile):
        mFile = open(logFile,'r')
        lines = mFile.readlines()
        for line in lines:
            for keyword in self.keywords:
                # logging.warning('current keyword: %s'%keyword[0] )
                key = keyword[1] + ' '
                if key in line:
                    logging.error('Found bug of catgeray: %s in log file: %s'%(keyword[0], logFile))
                    self.runningFlag = False
                    return

    def setRunningFlag(self, flag):
        self.runningFlag = flag

    def setLogFile(self):
        fileName = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time())) + '.log'
        self.logFile = fileName

    def updateAndDetach(self):
        while self.runningFlag:
            currentLogFile = self.logfilePath+os.sep+ self.logFile
            time.sleep(10)
            self.setLogFile()
            self.bugAssert(currentLogFile)

    def logSave(self, line):
        try:
            mFile = self.logfilePath+os.sep+ self.logFile
            # logging.warning(mFile)
            output = open(mFile, 'a')
            output.write(line)
            output.close()
        except Exception, e:
            output.close()
            logging.error(Exception, ":", e)

    def logcatGet(self):
        order = 'adb logcat -v time '
        handle = subprocess.Popen(order, shell=True, stdout=subprocess.PIPE)
        for line in iter(handle.stdout.readline, 'b'):
            self.logSave(line)
            # line = line.strip()
            # logging.info(line)
            if not self.runningFlag:
                break
        # subprocess.Popen("taskkill /F /T /PID " + str(handle.pid), shell=True)

if __name__ == '__main__':


    stMonitor =  BugDetach()
    # stMonitor.loadKeywords()
    # stMonitor.showKeywords()

    threads = []
    t1 = threading.Thread(target=stMonitor.logcatGet)
    threads.append(t1)
    t2 = threading.Thread(target=stMonitor.updateAndDetact)
    threads.append(t2)


    # set timer to stop monitor
    timer = threading.Timer(20.0, stMonitor.setRunningFlag, [False])
    timer.start()

    for t in threads:
        t.setDaemon(True)
        t.start()
    t.join()