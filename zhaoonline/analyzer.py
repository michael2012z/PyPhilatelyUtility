# -*- coding: utf-8 -*-
import sys
from HTMLParser import HTMLParser
import urllib, urllib2, cookielib
import os, time
import xml.dom.minidom

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.cbook as cbook
import matplotlib.ticker as ticker

from datetime import *  
#import locale
from decimal import Decimal
from re import sub

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from DataHandler import DataHandler
from HistoryItemParser import HistoryItemParser

# get history list
# get number of pages
# go through each page
# go through each item in page
# get the detail of each item
# analyze information of the item, title, comments, date, price, last prizing


# search list:
# text format:
# name, catalog\n

# search result:
# xml format:
# <history><item><id><name><comments><quality><date><price>


def main():
    user = None
    passwd = None
    if len(sys.argv) == 1:
        # offline mode
        user = None
        passwd = None
    elif len(sys.argv) == 3:
        user = sys.argv[1]
        passwd = sys.argv[2]
    else:
        print "ERROR: wrong count of parameter"
        print "Usage: "
        print "  python analyzer.py <user name> <password>"
        print "or offline mode: "
        print "  python analyzer.py"

    dataHandler = DataHandler(user, passwd)
    dataHandler.loadAllSearchItemsFromXml()
    quitCommand = False
    while quitCommand == False:
        command = raw_input("[z analyzer] ")
        parameters = command.split(' ', 4)
        if parameters[0] == "q" or parameters[0] == "quit" or parameters[0] == "exit":
            quitCommand = True
        elif parameters[0] == "list" or parameters[0] == "l":
            searchItems = dataHandler.getAllSearchItems()
            for searchItem in searchItems:
                print searchItem.name + "  -  " + searchItem.alias
#                print searchItem.name.decode("utf-8") + "  -  " + searchItem.alias
        elif parameters[0] == "add":
            def add(parameters):
                alias = parameters[1]
                name = parameters[2]
                category = parameters[3]
                quality = parameters[4]
                if cmp(category, '清代邮票') != 0 and cmp(category, '民国邮票') != 0 and cmp(category, '散票') != 0 and cmp(category, '纪特邮票') != 0 and cmp(category, '文革邮票') != 0 and cmp(category, '编号邮票') != 0 and cmp(category, 'JT邮票') != 0 and cmp(category, '任意') != 0:
                    print "ERROR: unknown category type: " + category
                elif cmp(quality, '全品') != 0 and cmp(quality, '上品') != 0 and cmp(quality, '任意') != 0:
                    print "ERROR: unknown quality type: " + quality
                else:
                    newSearchItem = dataHandler.addSearchItem(alias, name, category, quality)
                return

            # format: add <alias> <name> <category> <quality>
            if len(parameters) == 5:
                add(parameters)
            elif len(parameters) == 2 and parameters[1] == "all":
                f = open("queryList.txt")
                while True:
                    l = f.readline()
                    l = l.strip()
                    if not l:
                        break
                    if l[0] == '#':
                        continue
                    param = l.split(' ', 4)
                    if len(param) == 5:
                        add(param)
                f.close()
            else:
                print "ERROR: wrong count of parameter"

        elif parameters[0] == "show":
            # format: show <alias>
            if len(parameters) == 2:
                alias = parameters[1]
                searchItem = dataHandler.getSearchItemByAlias(alias)
                if searchItem == None:
                    print "ERROR: can't find alias: " + alias
                else:
                    price = []
                    date = []
                    # sort
                    historyItems = sorted(searchItem.historyItems, key=lambda x: x.date)
                    for historyItem in historyItems:
                        if cmp(searchItem.name, historyItem.name) == 0:
                            try:
                                d = datetime.strptime(historyItem.date, "%Y-%m-%d %H:%M:%S")
                                p = float(Decimal(sub(r'[^\d.]', '', historyItem.price))) 
                                if p == 0:
                                    continue
                                date.append(d)
                                price.append(p)
                            except Exception, e:
                                print e
                                continue
                    plt.plot(date, price)
                    plt.title(alias)
                    plt.ylabel('Price')
                    plt.xlabel('Date')
                    plt.grid(True)
                    plt.show()
            else:
                print "ERROR: wrong count of parameter"

        elif parameters[0] == "download":
            # format: download <alias>
            if len(parameters) == 2:
                if dataHandler.isOffLine():
                    print "ERROR: offline mode, can't download"
                    continue
                alias = parameters[1]
                if alias == 'all':
                    searchItems = dataHandler.getAllSearchItems()
                else:
                    searchItems = [dataHandler.getSearchItemByAlias(alias)]
                for searchItem in searchItems:
                    if searchItem == None:
                        print "ERROR: can't find alias: " + alias
                    else:
                        historyItems = sorted(searchItem.historyItems, key=lambda x: x.date)
                        downloadList = []
                        dirName = "image/" + searchItem.alias
                        if os.path.exists(dirName) == False:
                            os.mkdir(dirName)
                        elif os.path.isdir(dirName) == False:
                            print '"' + dirName + '" file exist, remove it'
                            continue
                            
                        # build download list at first
                        for historyItem in historyItems:
                            historyItemParser = HistoryItemParser()
                            (xxx, historyItem.auctionData) = historyItemParser.parsePureAuctionData(historyItem.auctionText)
                            #print historyItem.auctionData
                            for pictureData in historyItem.auctionData.get("pictures"):
                                #keys = ["src", "s1_size", "s2_size", "s3_size", "ss_size", "m_size"]
                                keys = ["src", "m_size"]
                                for key in keys:
                                    picURL = pictureData.get(key)
                                    if picURL <> None:
                                        picFileName = "image/" + searchItem.alias + "/" + picURL.split("/")[-3] + "_" + picURL.split("/")[-2] + "_" + picURL.split("/")[-1]
                                        downloadList.append([picURL, picFileName])
                        # then download image one by one
                        for i in range(0, len(downloadList)):
                            picURL = downloadList[i][0]
                            picFileName = downloadList[i][1]
                            try:
                                print "(" + str(i) + "/" + str(len(downloadList))+ ") downloading image: " + picURL
                                pic = dataHandler.download(picURL)
                                if pic <> None:
                                    picFile = open(picFileName, "wb")
                                    picFile.write(pic)
                                    picFile.close()
                            except Exception, e:
                                print e
                                continue
            else:
                print "ERROR: wrong count of parameter"


        elif parameters[0] == "up" or parameters[0] == "update":
            # format: show <alias>
            if len(parameters) == 2:
                if dataHandler.isOffLine():
                    print "ERROR: offline mode, can't update"
                    continue
                alias = parameters[1]
                if alias == 'all':
                    searchItems = dataHandler.getAllSearchItems()
                    for searchItem in searchItems:
                        print "updating searchItem: " + searchItem.name.decode("utf-8")
                        dataHandler.updateSearchItem(searchItem)
                        # debug
                        #dataHandler.dumpSearchItem(searchItem)
                    dataHandler.printLog()
                else:
                    searchItem = dataHandler.getSearchItemByAlias(alias)
                    if searchItem == None:
                        print "ERROR: can't find alias: " + alias
                    else:
                        print "updating searchItem: " + searchItem.name
                        dataHandler.updateSearchItem(searchItem)
                    dataHandler.printLog()
            else:
                print "ERROR: wrong count of parameter"

        elif parameters[0] == "save":
            # format: save <alias>
            if len(parameters) == 2:
                alias = parameters[1]
                if alias == "all":
                    dataHandler.saveAllSearchItemsToXml()
                    print "all data saved"
                else:
                    searchItem = dataHandler.getSearchItemByAlias(alias)
                    if searchItem == None:
                        print "ERROR: can't find alias: " + alias
                    else:
                        dataHandler.saveSearchItemToXml(searchItem)
                        print searchItem.alias + " data saved"
            else:
                print "ERROR: wrong count of parameter"

        else:
            print "ERROR: wrong command"




if __name__ == '__main__':
    main()
