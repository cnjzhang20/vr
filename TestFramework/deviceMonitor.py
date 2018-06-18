#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import os, logging, coloredlogs
# from adbExtend import adbExtend
import threading
import time


coloredlogs.install()

class activityLaunchInfo(object):
    def __init__(self, activityname, launchTime):
        self.activityName = activityname
        self.launchTime = launchTime

    def getActivityName(self):
        return self.activityName

    def getLaunchTime(self):
        return self.launchTime

    def lauchInfoShow(self):
        logging.warning('Activity: %s \t LaunchTime: %s' % (self.activityName, self.launchTime))


class RuningKPIInfo(object):
    def __init__(self, cpu, mem, powerConsulme):
        self.cpu = str(cpu)
        self.mem = str(mem)
        self.powerConsulme = str(powerConsulme)

    def KPIInfoShow(self):
        logging.warning( 'CPU %s\tMemory %s\tPowerConsulme %s'%(self.cpu, self.mem, self.powerConsulme))

class AppPerformanceInfo(object):

    pck_name = ''
    def __init__(self, packageName=''):
        self.pkg_name = packageName
        self.runingFlag = True
        self.actInfo = []
        self.resourceInfo = []

    def setRunningFlag(self,flag):
        self.runingFlag = flag


    # get cpu occupy of specific package
    def dump_cpu_byTop(self):
        cpu = 0
        pids = self.getPackgeRunningPID()
        cmd = "adb shell top -n 1"

        top_info = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()
        cpuSum = 0.0
        try:
            for line in top_info:
                # print info.strip()
                for pid in pids:
                    pid = str(pid)
                    if pid in line:
                        logging.warning( line.strip())
                        for info in line.strip().split(' '):
                            if '%' in info:
                                logging.warning( '------------------>' + str(info))
                                cpu = float(info.split('%')[0])
                                cpuSum = cpuSum+cpu

        except Exception, e:
            logging.error( Exception, ":", e)

        logging.warning("CPU usage: %.1f" %cpuSum)
        return cpuSum

    # get cpu occupy of specific package
    def dump_cpu(self):
        cpu = 0
        cmd = "adb shell dumpsys cpuinfo | grep %s" %(self.pkg_name)
        # print cmd

        top_info = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()
        cpuSum = 0.0
        try:
            for info in top_info:
                # print info.strip()
                cpu = float(info.split('%')[0])
                cpuSum = cpuSum + cpu
        except Exception, e:
            logging.error(Exception, ":", e)

        logging.warning("CPU usage: %.1f" %cpuSum)
        return cpuSum

    # get memory occupy of specific package
    def dump_men_PSS(self):
        cmd = "adb shell dumpsys meminfo %s" %(self.pkg_name)
        # print (cmd)

        men_s = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()
        mem = '0'
        try:
            for info in men_s:
                if 'TOTAL:' in info:
                    mem = info.split()[1]
        except Exception, e:
            logging.error( Exception, ":", e)
        logging.warning("MEM usage: %s"%mem +" KB")
        return mem

    def getResourceInfo(self):
        while self.runingFlag:
            cpu = self.dump_cpu_byTop()
            mem = self.dump_men_PSS()
            power = self.getPowerConsulme()
            kpi = RuningKPIInfo(cpu, mem,power)
            self.resourceInfo.append(kpi)
            time.sleep(3)

    # def get_currentActivity(self):

    def get_activityLuanchTime(self):

        cmd = "adb logcat "
        p = subprocess.Popen(cmd , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while self.runingFlag:
            line = p.stdout.readline().strip()
            if "ActivityManager: Displayed" in line:
                activity = line.split('Displayed')[1].split(':')[0]
                launchTime = line.split('+')[1].split('ms')[0]
                logging.warning( 'Activity: %s \t LaunchTime: %s' %(activity, launchTime))
                currentLuanchInfo = activityLaunchInfo(activity, launchTime)
                self.actInfo.append(currentLuanchInfo)
                logging.warning( self.runingFlag)

                # get activity fps
                self.getFPSN(activity)

    def showLaunchInfo(self):
        logging.warning( '--------- Activity Launch Information---------')
        for mInfo in self.actInfo:
            mInfo.lauchInfoShow()

    def showKPIInfo(self):
        logging.warning( '--------- System Resource Information---------')
        for mInfo in self.resourceInfo:
            mInfo.KPIInfoShow()

    def getGFX(self,activityName):
        command = 'shell dumpsys gfxinfo %s'%activityName
        command2 = 'shell dumpsys gfxinfo --clear'
        command_text = 'adb %s' % command
        results = os.popen(command_text, "r")

        try:
            while True:
                line = results.readline()

                if not line:
                    break
                else:
                    logging.warning( line)

        except Exception, e:
            logging.error(Exception, ":", e)

        command_text = 'adb %s' % command2
        os.popen(command_text, "r")


    def getFPSO(self,activityName):
        command = 'shell dumpsys SurfaceFlinger --latency %s'%activityName
        command2 = 'shell dumpsys SurfaceFlinger --latency-clear'
        command_text = 'adb %s' % command
        results = os.popen(command_text, "r")

        try:
            frameNumber = 1
            startTime = 0
            endTime = 0
            while True:
                line = results.readline()

                if not line:
                    break
                elif line.split('\t')[0] != '0':
                    if '\t' not in line and len(line)>1:
                        nanoseconds_per_second = 1e6
                        refresh_period = long(line) / nanoseconds_per_second
                        logging.warning( 'refresh-period: %d ms' %(refresh_period))
                    elif len(line)>1:
                        logging.warning( line.strip())
                        timeA = int(line.strip().split('\t')[0])
                        timeC = int(line.strip().split('\t')[2])
                        logging.warning( 'Timeslot %d:  %d'%(frameNumber,timeC-timeA))
                        frameNumber = frameNumber+1
                        if startTime == 0:
                            startTime = timeA
                        endTime = timeC
            logging.warning( 'endTime: %d'%endTime)
            logging.warning( 'startTime: %d'%startTime)

            totalTime = (endTime-startTime)/1000/1000
            totalFrame = frameNumber-1
            logging.warning( 'TOTAL TIME: %d, TotalFrame:%d, FPS %d'%(totalTime,totalFrame, totalFrame*1000/totalTime))
            # print 'fps: %d ms'%(endTime-startTime)/int(lineNumber-1)/1000/1000

        except Exception, e:
            logging.error( Exception, ":", e)

        command_text = 'adb %s' % command2
        os.popen(command_text, "r")

    def getFPSN(self,activityName):
        command = 'shell dumpsys SurfaceFlinger --latency %s'%activityName
        command2 = 'shell dumpsys SurfaceFlinger --latency-clear'
        command_text = 'adb %s' % command
        results = os.popen(command_text, "r")

        try:
            frameNumber = 1
            startTime = 0
            endTime = 0
            while True:
                line = results.readline()
                if not line:
                    break
                elif len(line)<2:
                    continue
                elif line.strip('\t')[0] == '0':
                    continue
                elif '\t' not in line:
                    nanoseconds_per_second = 1e6
                    refresh_period = long(line) / nanoseconds_per_second
                    logging.warning( 'refresh-period: %d ms' % (refresh_period))
                else:
                    # print line.strip()
                    timeA = int(line.strip().split('\t')[0])
                    timeC = int(line.strip().split('\t')[2])
                    # print 'Timeslot %d:  %d' % (frameNumber, timeC - timeA)
                    frameNumber = frameNumber + 1
                    if startTime == 0:
                        startTime = timeA
                    endTime = timeC

            # print 'endTime: %d'%endTime
            # print 'startTime: %d'%startTime

            totalTime = (endTime-startTime)/1000/1000
            totalFrame = frameNumber-1
            if totalTime != 0:
                fps = totalFrame*1000/totalTime
            else:
                fps = 1

            logging.warning( 'TOTAL TIME: %d, TotalFrame:%d, FPS %d'%(totalTime,totalFrame, fps))

        except Exception, e:
            logging.error(Exception, ":", e)

        command_text = 'adb %s' % command2
        os.popen(command_text, "r")

    # get ps user/uid of the current package by command adb shell ps
    # user/uid format from ps is: u0_a21, will changed to format u0a21 to fit powerconsulme format.
    def getPackageRunningPSUsers(self):
        if self.pkg_name == None:
            return None
        psUsers = []
        packageName = self.pkg_name
        cmd = "adb shell ps"
        out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()
        try:
            for line in out:
                if packageName in line:
                    user = line.split()[0]
                    user = str(user).replace('_', '')
                    if user not in psUsers:
                        psUsers.append(user)
        except Exception, e:
            logging.error( Exception, ":", e)
        return psUsers

    def getPackgeRunningPID(self):
        if self.pkg_name == None:
            return None
        PIDs = []
        packageName = self.pkg_name
        cmd = "adb shell ps"
        out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()
        try:
            for line in out:
                if packageName in line:
                    user = line.split()[1]
                    PIDs.append(user)
        except Exception, e:
            logging.error( Exception, ":", e)
        return PIDs

    def getPowerConsulme(self):
        psUsers = self.getPackageRunningPSUsers()
        if psUsers == None:
            return None
        powerCons = ''
        cmd = 'adb shell dumpsys batterystats'
        out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.readlines()
        try:
            for line in out:
                for user in psUsers:
                    keywords = 'Uid '+ user
                    if keywords in line:
                        powerCons = line.split(':')[1].strip()
                        logging.warning( 'Power:' + str(powerCons))
        except Exception, e:
            logging.error( Exception, ":", e)
        return powerCons

    def getPowerInfo(self):
        while self.runingFlag:
            self.getPowerConsulme()
            time.sleep(3)

if __name__ == '__main__':

    devicePerf = AppPerformanceInfo('com.android.chrome')

    # set thread for monitor
    threads = []
    t1 = threading.Thread(target=devicePerf.getResourceInfo)
    threads.append(t1)
    t2 = threading.Thread(target=devicePerf.get_activityLuanchTime)
    threads.append(t2)


    # set timer to stop monitor
    timer = threading.Timer(100.0, devicePerf.setRunningFlag, [False])
    timer.start()

    for t in threads:
        t.setDaemon(True)
        t.start()

    t.join()

    logging.warning( '---------------------------')
    devicePerf.showLaunchInfo()
    devicePerf.showKPIInfo()
