#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

from pyadb.adb import ADB
import Image
import os, time, logging
# from deviceMonitor import AppPerformanceInfo
# import AppPerformanceInfo
import deviceMonitor

# device connection check

class adbExtend(object):

    def commands(self, commands):
        command_result = ''
        command_text = commands
        results = os.popen(command_text, "r")
        while 1:
            line = results.readline()
            if not line:
                break
            command_result += line
        results.close()
        return command_result

    def call_adb(self, command):
        command_result = ''
        command_text = 'adb %s' % command
        results = os.popen(command_text, "r")
        while 1:
            line = results.readline()
            if not line:
                break
            command_result += line
        results.close()
        return command_result

    def attached_devices(self):
        result = self.call_adb("devices")
        devices = result.partition('\n')[2].replace('\n', '').split('\tdevice')

        if len(devices)>1 and len(devices)<3:
            return devices[0]
        elif len(devices)<2:
            return 'Warning, no devices connected.'
        else:
            return 'Warning, more than 1 devices found.'

    # def showDevices(self):
    #
    #     myadb = ADB('/usr/bin/adb')
    #     device = myadb.get_devices()
    #     if device[0] != 0:
    #         print 'connect device error'
    #     else:
    #         print 'device count: %d'%(len(device[1]))
    #         for i in device[1]:
    #             print 'Device Serial No: ' + i


    # 状态
    def get_state(self):
        result = self.call_adb("get-state")
        result = result.strip(' \t\n\r')
        return result or None


    # push file from computer to device
    def push(self, local, remote):
        result = self.call_adb("push %s %s" % (local, remote))
        return result

    # pull file from device to computer
    def pull(self, remote, local):
        result = self.call_adb("pull %s %s" % (remote, local))
        return result

    # sync
    def sync(self, directory, **kwargs):
        command = "sync %s" % directory
        if 'list' in kwargs:
            command += " -l"
            result = self.call_adb(command)
            return result

    # luanch app with package name and activity
    def open_app(self,packagename,activity):
        result = self.call_adb("shell am start -n %s/%s" % (packagename, activity))
        check = result.partition('\n')[2].replace('\n', '').split('\t ')
        if check[0].find("Error") >= 1:
            return False
        else:
            return True

    def get_resolution(self):
        result = self.call_adb("shell wm size")
        x = str(result).split(':')[1].split('x')[0].strip()
        y = str(result).split('x')[1].strip()
        print 'x = %s, y = %s'%(x, y)

        return x, y

    # for android N
    def getCurrentActivityN(self):
        command = 'shell dumpsys activity'
        command_result = ''
        command_text = 'adb %s' % command
        results = os.popen(command_text, "r")
        currentAct = ''
        while 1:
            line = results.readline()
            if not line:
                break
            if 'mFocusedActivity' in line:
                # print line
                currentAct = line.split(' ')[-2]
                break
        results.close()
        return currentAct

    # for android O
    def getCurrentActivityO(self):
        command = 'shell dumpsys window windows'
        command_text = 'adb %s' % command
        results = os.popen(command_text, "r")
        currentAct = ''
        while 1:
            line = results.readline()
            if not line:
                break
            if ('name=' in line) and ('/' in line):
                # print line
                currentAct = line.split('name=')[1].split(')')[0]
                break
        results.close()
        return currentAct


    def getCurrentTopView(self):
        command = 'shell dumpsys activity top'
        command_result = ''
        command_text = 'adb %s' % command
        results = os.popen(command_text, "r")
        currentView = ''
        try:
            while 1:
                line = results.readline()
                if not line:
                    break
                if 'mView' in line:
                    # print line
                    currentView = line.strip().split('{')[1].split('}')[0]
                    break
            results.close()
        except Exception, e:
            print Exception, ":", e

        return currentView

    def monkeyTest(self, packageName,times):
        monkeyCMD = 'shell monkey -p %s --throttle 200 %d'%(packageName,times)
        logging.info('------ Start Monkey Test ---------')
        logging.info('Command: %s'%monkeyCMD)
        result = self.call_adb(monkeyCMD)
        logging.info('------ Monkey Test Finished ---------')
        return

    def startActivity(self, activityName):
        result = self.call_adb("shell am start -W %s"%activityName)
        return

    def stopActivity(self, packageName):
        result = self.call_adb("shell am force-stop %s"%packageName)
        return

    def touchEvent(self, x, y):
        print 'touch %d %d'%(x,y)
        command = 'shell input tap %d %d'%(x,y)
        self.call_adb(command)

    def getSnapshot(self, picName):
        cmd1 = 'shell screencap -p /sdcard/screenshot.png'
        cmd2 = 'pull /sdcard/screenshot.png screenshot.png'
        print 'take snapshot ...'
        self.call_adb(cmd1)
        self.call_adb(cmd2)
        print 'convert to jpeg ...'
        image = Image.open("screenshot.png")
        image.save(picName)

if __name__ == '__main__':
    adb = adbExtend()
    # deviceSerial = adb.attached_devices()
    # print 'device: ' + deviceSerial

    # print adb.getCurrentActivity()
    # print adb.getCurrentTopView()
    # adb.getSnapshot('1.jpeg')
    # print adb.getCurrentActivityN()

    actName = adb.getCurrentActivityO()
    print actName
    # adb.getFpsByPylib(actName)
    appP = deviceMonitor.AppPerformanceInfo()
    appP.getFPSN(actName)
    appP.getGFX(actName)
    # adb.showDevices()
    # adb.get_state()

    # adb.execShellCommand('adb shell uiautomator dump --compressed')
    # adb.execShellCommand('adb pull /sdcard/window_dump.xml .')
    # adb.call_adb('root')
    # adb.call_adb('shell uiautomator dump --compressed')
    # adb.call_adb('pull /sdcard/window_dump.xml .')

    # if 'Warning' not in adb.attached_devices():
    #     performancInfo = AppPerformanceInfo('com.android.camera2')
    #     performancInfo.top_cpu()
    #     # performancInfo.get_men()
    #     performancInfo.get_activityLuanchTime()
    # else:
    #     print(" ---------- please connect android device ------------- ")

    # adb.get_resolution()
