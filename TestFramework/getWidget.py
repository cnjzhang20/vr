# -*- coding: utf-8 -*-
#!/usr/bin/env python

import time
import subprocess
import locale
import codecs
import os
import multiprocessing
# import FileRW
import socket, sys
from adbExtend import adbExtend
import xml.sax
# import xml.dom.minidom
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import parse
# import testAutomator


def activityDump(filename = 'tmp.xml'):
    strRoot = 'adb root'
    strDumpXML = "adb shell uiautomator dump /data/local/tmp/uidump.xml"
    strPullXML = "adb pull /data/local/tmp/uidump.xml " + filename

    adb = adbExtend()
    # deviceSerial = adb.attached_devices()
    # print 'device: ' + deviceSerial
    # adb.showDevices()
    # adb.get_state()

    adb.commands(strRoot + ' ; ' + strDumpXML+' ; ' + strPullXML)

    # adb.execShellCommand('adb shell uiautomator dump --compressed')
    # adb.execShellCommand('adb pull /sdcard/window_dump.xml .')
    # adb.call_adb('root')
    # adb.call_adb(strDumpXML)
    # adb.call_adb(strPullXML)
    # print ('---------- waiting for your next event --------------')


def xmlAnalysis(x, y):

    f = open('tmp.xml', 'r')
    tree = ET.parse(f)
    root = tree.getroot()

    # print ('root.tag =', root.tag)
    # print ('root.attrib =', root.attrib)

    miniSize = 0
    miniNode = None
    for child in root.iter('node'):
        # print '------- ' + str(count) + ' -------'
        # print (child.tag)
        # print (child.attrib)

        bounds = child.get('bounds')
        size = boundsMatch(x,y,bounds)
        if size != -1:
            if miniSize == 0:
                miniSize = size
                miniNode = child
            elif size < miniSize:
                miniSize = size
                miniNode = child

    if miniNode is not None:

        index = miniNode.get('index')
        text = miniNode.get('text')
        resourceid = miniNode.get('resource-id')
        myclass = miniNode.get('class')
        package = miniNode.get('package')
        contentdesc = miniNode.get('content-desc')
        checkable = miniNode.get('checkable')
        checked = miniNode.get('checked')
        clickable = miniNode.get('clickable')
        enabled = miniNode.get('enabled')
        focusable = miniNode.get('focusable')
        focused = miniNode.get('focused')
        scrollable = miniNode.get('scrollable')
        longclickable = miniNode.get('long-clickable')
        password = miniNode.get('password')
        selected = miniNode.get('selected')
        bounds = miniNode.get('bounds')

        print ('index: ' + index)
        print ('text: ' + text)
        print ('resourceid: ' + resourceid)
        print ('class: ' + myclass)
        print ('package: ' + package)
        print ('content-desc: ' +  contentdesc)
        print ('checkable: ' + checkable)
        print ('checked: '+ checked)
        print ('clickable: ' + clickable )
        print ('enable: ' + enabled)
        print ('focusable: ' + focusable)
        print ('focused: ' +  focused)
        print ('scrollable: ' + scrollable)
        print ('long-click: '+ longclickable)
        print ('password: ' + password)
        print ('selected: '+ selected)
        print ('bounds: ' + bounds )

        return miniNode
    else:
        print ('-------------------------')
        print ('---  wight not found ----')
        print ('-------------------------')
        return None

# # home, back, menu, enter, volume_up, volume_down, volume_mute, camera, power
# def sysKeyCaseWrite(key):
#     sysKeys = ['home', 'back', 'menu', 'enter', 'volum_up', 'volum_down', 'volum_mute', 'camera', 'power']
#     if key in sysKeys:
#         testAutomator.systemKey(key)

# def dragCaseWrite(x0,y0,x1,y1):
#
#     print ("Drag Event: x0=%d , y0=%d , x1=%d , y1=%d" % (x0, y0, x1, y1))
#     testAutomator.androidEvent('true', 'false', 'false', 'false',
#                                'flase', 'flase', 'flase', 'false',
#                                'flase', x0, y0, x1, y1)

# def touchCaseWrite(x,y):
#
#     print ("Touch Event: x=%d , y=%d" % (x, y))
#     miniNode = xmlAnalysis(x, y)
#
#     if miniNode is not None:
#
#         index = miniNode.get('index')
#         text = miniNode.get('text')
#         resourceid = miniNode.get('resource-id')
#         myclass = miniNode.get('class')
#         package = miniNode.get('package')
#         contentdesc = miniNode.get('content-desc')
#         checkable = miniNode.get('checkable')
#         checked = miniNode.get('checked')
#         clickable = miniNode.get('clickable')
#         enabled = miniNode.get('enabled')
#         focusable = miniNode.get('focusable')
#         focused = miniNode.get('focused')
#         scrollable = miniNode.get('scrollable')
#         longclickable = miniNode.get('long-clickable')
#         password = miniNode.get('password')
#         selected = miniNode.get('selected')
#         bounds = miniNode.get('bounds')
#
#         testAutomator.androidEvent('false', focusable, longclickable, clickable,
#                                        contentdesc, text, index, resourceid,
#                                        password,0,0,0,0)
#         xmlDump()

def boundsMatch(x,y, bounds):

    x0 = bounds.split(',')[0].replace('[','')
    y0 = bounds.split('][')[0].split(',')[1]
    x1 = bounds.split('][')[1].split(',')[0]
    y1 = bounds.split(',')[2].replace(']','')


    if(x>int(x0) and x<int(x1) and y>int(y0) and y<int(y1)):
        # print ('x0=%s,y0=%s,x1=%s,y1=%s' % (x0, y0, x1, y1))
        return (int(x1)-int(x0))*(int(y1)-int(y0))

    else:
        return -1


if (__name__ == "__main__"):

    activityDump('tmp1.xml')
    # xmlAnalysis()