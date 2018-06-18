#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import getWidget
from drawPic import drawPic
from adbExtend import adbExtend
from deviceMonitor import AppPerformanceInfo
from bugDetect import BugDetect
import os, logging, coloredlogs
import time,threading

coloredlogs.install()

# view (activity) structure
class View(object):

    def __init__(self, level=0, actName='', topView='', father='', nodes=None):
        # self.id = id

        self.index = actName+topView
        self.level = level
        self.actName = actName
        self.packgeName = actName.split('/')[0]
        self.father = father
        self.topView = topView
        self.notes = []
        # mn = node()
        for mn in nodes:
            self.notes.append(mn)

    def getIndex(self):
        return self.index

    def getActName(self):
        return self.actName

    def getPackgaName(self):
        return self.packgeName

    # Get current frame layout to identify activity and content change.
    def getTopView(self):
        return self.topView

    def getNotes(self):
        return self.notes

    def getLevel(self):
        return self.level

    def setFather(self, father):
        self.father = father

    def setLevel(self, level):
        self.level = level

    def showView(self,showNodesFlag=False):
        logging.info('--------------------- start -----------------------------')
        logging.info( 'Current View: %s, level: %d, father: %s, node list as bellow'%(self.actName, self.level, self.father) )

        sumNodes = len(self.notes)
        travedNode = 0
        for mn in self.notes:
            if showNodesFlag:
                mn.showNode()
            if not mn.getStatus():
                travedNode = travedNode+1
        logging.info('Current Nodes, Sum:%d, Already Traveled: %d'%(sumNodes,travedNode) )
        logging.info('---------------------- end  ----------------------------')


# node structure
# description for widget on view(activity)
# as node list, involved in view
class Node(object):

    def __init__(self, id, bounds='[0,0][0,0]', text='', status=True, type=''):

        self.id = id
        self.type = type
        self.status = status
        self.path = id
        self.bounds = bounds
        self.text = text
        self.x0 = int(bounds.split(',')[0].replace('[', ''))
        self.y0 = int(bounds.split(',')[1].split('][')[0])
        self.x1 = int(bounds.split(',')[1].split('][')[1])
        self.y1 = int(bounds.split(',')[2].replace(']', ''))
        self.xcenter = (int(self.x0) + int(self.x1))/2
        self.ycenter = (int(self.y0) + int(self.y1))/2

    def getX0(self):
        return self.x0

    def getX1(self):
        return self.x1

    def getY0(self):
        return self.y0

    def getY1(self):
        return self.y1

    def getXcenter(self):
        return self.xcenter

    def getYcenter(self):
        return self.ycenter

    def getID(self):
        return self.id

    def getPath(self):
        return self.path

    def getStatus(self):
        return self.status

    def getText(self):
        return self.text

    def setStatus(self, status):
        self.status = status

    def showNode(self):
        logging.info('Current Node %s, bounds: %s, text: %s, status: %s, type: %s'%(self.id, self.bounds,self.text, self.status, self.type))

class viewAnalysis(object):

    def getCurrentView(self):

        adb = adbExtend()
        actName = adb.getCurrentActivityO()
        topView = adb.getCurrentTopView()
        nodes =self.getNodes()
        mView = View(actName=actName, topView=topView, nodes=nodes)
        return mView

    def getNodes(self):

        fileName = 'tmp.xml'
        getWidget.activityDump(fileName)
        f = open('./'+fileName, 'r')
        tree = ET.parse(f)
        root = tree.getroot()

        mNodes = []
        widgetNumber = 1

        for child in root.iter('node'):
            if 'true' in child.attrib['clickable']:
                # print child.attrib
                try:
                    # print '----childrens----'
                    mBounds = child.attrib.get('bounds')
                    mClass = child.attrib.get('class')
                    # print 'bounds:' + str(mBounds)
                    # print 'class' + str(mClass)

                    mNode = Node(widgetNumber,mBounds,type=mClass)
                    mNodes.append(mNode)
                    widgetNumber = widgetNumber + 1

                except Exception, e:
                    logging.error( Exception, ":", e)

        return mNodes

    def drawView(self, mView):

        dpic = drawPic()
        picFile = mView.getActName().split('.')[-1]
        picFile = picFile+ '.jpeg'
        logging.info ('Draw view as file: %s'%picFile)

        adb = adbExtend()
        [xmax, ymax] = adb.get_resolution()
        dpic.createPic(int(xmax), int(ymax), picFile)
        adb.getSnapshot(picFile)

        for mn in mView.getNotes():
            x0 = mn.getX0()
            y0 = mn.getY0()
            x1 = mn.getY1()
            y1 = mn.getY1()
            xcenter = mn.getXcenter()
            ycenter = mn.getYcenter()
            mText = mn.getText()
            mID = mn.getID()
            dpic.drawRec(x0,y0,x1,y1, picFile)
            dpic.drawText(x0,y0, mText, picFile)
            dpic.drawText(xcenter, ycenter, str(mID), picFile)


    # for test, show all wighet of current activity
    def phaseXML(self, fileName):

        getWidget.activityDump(fileName)

        f = open('./'+fileName, 'r')
        tree = ET.parse(f)
        root = tree.getroot()

        logging.info('root.tag =', root.tag)
        logging.info('root.attrib =', root.attrib)

        miniSize = 0
        miniNode = None

        dpic = drawPic()
        picFile = 'activity.jpeg'

        adb = adbExtend()
        [xmax, ymax] = adb.get_resolution()
        dpic.createPic(int(xmax), int(ymax), picFile)

        widgetNumber = 1

        for child in root.iter('node'):

            logging.info( '------- ×××××××××××××××××××××××××××××××× -------')
            # print (child.tag)
            # print (child.attrib)

            if 'true' in child.attrib['clickable']:
                logging.info( child.attrib)
                logging.info( '----childrens----')
                bounds = child.attrib.get('bounds')
                mClass = child.attrib.get('class')
                logging.info( 'bounds:' + str(bounds))
                logging.info( 'class:' + str(mClass))

                try:
                    x0 = bounds.split(',')[0].replace('[', '')
                    y0 = bounds.split(',')[1].split('][')[0]
                    x1 = bounds.split(',')[1].split('][')[1]
                    y1 = bounds.split(',')[2].replace(']', '')

                    dpic.drawRec(int(x0), int(y0), int(x1), int(y1), picFile)
                    dpic.drawText(int(x0), int(y0), child.attrib.get('text'), picFile)

                    xcenter = (int(x0) + int(x1))/2
                    ycenter = (int(y0) + int(y1))/2
                    dpic.drawText(int(xcenter), int(ycenter), str(widgetNumber), picFile)
                    widgetNumber = widgetNumber+1
                    # dpic.drawText(int(x0), int(y0)+40, child.attrib.get('resource-id'), picFile)

                except Exception, e:
                    logging.error(Exception, ":", e)

            else:
                logging.info( 'current widget unclickable')
                logging.info( child.attrib)
                logging.info( '----childrens----')
                bounds = child.attrib.get('bounds')
                logging.info( 'bounds:' + str(bounds))

                try:
                    x0 = bounds.split(',')[0].replace('[', '')
                    y0 = bounds.split(',')[1].split('][')[0]
                    x1 = bounds.split(',')[1].split('][')[1]
                    y1 = bounds.split(',')[2].replace(']', '')

                    dpic.drawRec(int(x0), int(y0), int(x1), int(y1), picFile, col='blue')
                    # dpic.drawText(int(x0), int(y0)+40, child.attrib.get('resource-id'), picFile)

                except Exception, e:
                    logging.error( Exception, ":", e)

class viewTree(object):

    def __init__(self):
        self.mViewList = []

    # rootFile = '/home/john/test'

    def addView(self, mView):
        self.mViewList.append(mView)

    def findView(self, viewIndex):
        mView = None
        for mV in self.mViewList:
            if mV.getIndex() == viewIndex:
                mView = mV
                break
        return mView

    def checkViewExist(self, mView):
        viewExistFlag = False
        for mV in self.mViewList:
            if mV.getIndex() == mView.getIndex():
                viewExistFlag = True
                break;
        return viewExistFlag


class viewTraversal(object):

    def __init__(self, maxLevel = 3):
        self.maxLevel = maxLevel
        self.mViewTree = viewTree()

    def mutiLuanchApp(self, activityName, packageName, times):
        for i in range(times):
            adbExtend().stopActivity(packageName)
            time.sleep(1)
            adbExtend().startActivity(activityName)
            time.sleep(1)

    def startTravelView(self):

        level = 1

        # adb = adbExtend()
        viewAna = viewAnalysis()
        self.rootView = viewAna.getCurrentView()
        self.rootView.setFather('ROOT')
        self.rootView.setLevel(level)
        self.rootView.showView()

        self.mutiLuanchApp(self.rootView.getActName(), self.rootView.getPackgaName(), 3)
        self.travelCurrentView(self.rootView)
        adbExtend().monkeyTest(self.rootView.getPackgaName(), 1000)

    def travelCurrentView(self, mView):

        # check current view is a new view or not
        # if yes, add the newview to view list, then start to travel it
        # if not, replace the view with old view in view list, continue to travel it
        if self.mViewTree.checkViewExist(mView):
            viewIndex = mView.getIndex()
            mView = self.mViewTree.findView(viewIndex)
            logging.info( '***** --- current view existed, replace it with old view in view list')
            logging.info( 'view name %s'%mView.getActName())
            # mView.showView()
        else:
            self.mViewTree.addView(mView)

        currentLevel = mView.getLevel()

        if currentLevel > self.maxLevel:
            logging.info( 'current level is bigger than max level, current test stop')
            logging.info( 'current level: %d, max level: %d'%(currentLevel, self.maxLevel))
            return
        else:
            logging.info( 'level match, continue testing ')

        rootAct = self.rootView.getActName()
        rootPackage = self.rootView.getPackgaName()

        currentAct = mView.getActName()
        currentView = mView.getTopView()


        for mNode in mView.getNotes():

            # set node status to false, that means the node has been touched(traveled) already
            if mNode.getStatus():
                mNode.setStatus(False)
                actName = adbExtend().getCurrentActivityO()
                viewName = adbExtend().getCurrentTopView()
                if not rootPackage==actName.split('/')[0]:
                    adbExtend().startActivity(rootAct)
                    return

                self.enterSan(mNode)

                # compare new view and old view with activity and topview.
                # activity not match, means view changed
                logging.info( '-------->Activity name: ' + actName)
                if not(currentAct == actName):
                    logging.info( '**** Activity not compared******************')
                    logging.info( 'old: ' + currentAct)
                    logging.info( 'new: ' + actName)

                    sanView = viewAnalysis().getCurrentView()
                    sanView.setLevel(currentLevel+1)
                    sanView.setFather(currentAct)
                    self.travelCurrentView(sanView)
                    # self.backKey()

                # activity match but top view not match, means content changed, also assert as a new view
                elif not(currentView == viewName):
                    logging.info( '**** Activity compare ***********************')
                    logging.info( '**** **** TopView not compared******************')
                    logging.info( 'old: ' + currentView)
                    logging.info( 'new: ' + viewName)
                    # self.backKey()
                    sanView = viewAnalysis().getCurrentView()
                    sanView.setLevel(currentLevel+1)
                    sanView.setFather(currentAct)
                    self.travelCurrentView(sanView)

            mView.showView()

        self.backKey()


    def backKey(self):
        logging.info( '--------> back to father view')
        adbExtend().call_adb('shell input keyevent KEYCODE_BACK')

    def enterSan(self, sunNode):
        # mpth = sunNode.getPath()
        logging.info( 'Enter san--------')
        xcenter = sunNode.getXcenter()
        ycenter = sunNode.getYcenter()
        adbExtend().touchEvent(xcenter, ycenter)
        time.sleep(1)

    # def startTraversalFolder(self, dir, level=0, father='ROOT'):
    #     # print 'startTraversal'
    #
    #     level = level + 1
    #     # print 'level: %d, node: %s'%(level, dir)
    #     filelist = os.listdir(dir)
    #     mNodes = []
    #
    #     for mnID in filelist:
    #         mNode = Node(mnID, 'false','folder')
    #         mNodes.append(mNode)
    #         self.enterSan(mNode)
    #
    #     mView = View(level,dir, father, mNodes)
    #     mView.showView()
    #
    #     for i in filelist:
    #         fullfile = os.path.join(dir, i)
    #         if not os.path.isdir(fullfile):
    #             print 'level: %d, leaf: %s'%(level, fullfile)
    #         else:
    #             self.startTraversalFolder(fullfile, level,dir)



if __name__ == '__main__':

    beforeTime = time.time()

    # Prepare for device monitor
    activityName = adbExtend().getCurrentActivityN()
    packageName = activityName.split('/')[0]
    devicePerf = AppPerformanceInfo(packageName)

    # Prepare for bug detach
    bugDetach = BugDetach()

    # set thread for monitor
    threads = []
    t1 = threading.Thread(target=devicePerf.getResourceInfo)
    threads.append(t1)
    t2 = threading.Thread(target=devicePerf.get_activityLuanchTime)
    threads.append(t2)

    # bug detach thread
    t3 = threading.Thread(target=bugDetach.logcatGet)
    threads.append(t3)
    t4 = threading.Thread(target=bugDetach.updateAndDetach)
    threads.append(t4)

    # start device monitor thread
    for t in threads:
        t.setDaemon(True)
        t.start()
    # t.join()

    # activity travel test thread
    mViewTravs = viewTraversal(maxLevel=3)
    mViewTravs.startTravelView()

    # stop device monitor and bug detach
    devicePerf.setRunningFlag(False)
    bugDetach.setRunningFlag(False)

    logging.info( '----------- show some result ----------------')
    devicePerf.showLaunchInfo()
    devicePerf.showKPIInfo()

    afterTime = time.time()
    logging.info( time.strftime('Excute Time: %d s'%(afterTime-beforeTime)))


