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

from DataType import SearchData
from DataType import SearchItem
from DataType import categoryDic
from DataType import qualityDic
from DataType import HistoryItem
from HtmlDownloader import HtmlDownloader
from SearchResultHandler import SearchResultXmlLoader
from SearchResultHandler import SearchResultXmlGenerator
from HistoryItemListParser import HistoryItemListParser
from HistoryItemParser import HistoryItemParser

class DataHandler():
    searchData = None
    downloader = None
    failureList = []

    def __init__(self, user, passwd):
        self.searchData = SearchData()
        self.downloader = HtmlDownloader(user, passwd)
    
    def isOffLine(self):
        return self.downloader.isOffLine()

    def download(self, url):
        return self.downloader.downLoad(url)

    def printLog(self):
        print "failure records: "
        for failure in self.failureList:
            print "  " + failure
        self.failureList = []
        
    def addSearchItem(self, alias, name, category, quality):
        newItem = SearchItem()
        newItem.alias = alias
        newItem.name = name
        newItem.category = category
        newItem.quality = quality
        for item in self.searchData.searchItems:
            if cmp (newItem.alias, item.alias) == 0 or (cmp(newItem.name, item.name) == 0 and cmp(newItem.category, item.category) and cmp(newItem.quality, item.quality)):
                print "exist"
                return item
        self.searchData.searchItems.append(newItem)
        return newItem

    def getSearchItemURL(self, searchItem, page):
        url = "http://www.zhaoonline.com/search/"
        url += urllib.pathname2url(searchItem.name)
        url += "-8-3-trade-"
        url += urllib.pathname2url(categoryDic[searchItem.category])
        url += "-"
        url += urllib.pathname2url(qualityDic[searchItem.quality])
        url += "-00-N-0-N-1-"
        url += str(page)
        url += ".htm"
        return  url

    def getHistoryItemURL(self, ref):
        url = "http://www.zhaoonline.com"
        url += ref
        return url

    def updateSearchItem(self, searchItem):
        page = 1
        historyItemListParser = HistoryItemListParser()
        while historyItemListParser.hasNextPage(page):
            url = self.getSearchItemURL(searchItem, page)
            print "parsing search list: " + url
            html = self.downloader.getHtml(url)
            if html == None:
                break
            #html = self.downloader.download(url)
            if historyItemListParser.parse(html) == False:
                self.failureList.append(url)
            self.saveToListFile(searchItem.name+"_"+str(page), html)
            page += 1
        historyItemList = historyItemListParser.getHistoryItemList()
        historyItemListParser.clean()
        searchItem.historyItems = historyItemList
        # now every HistoryItem has id only
        for i in range(0, len(searchItem.historyItems)):
            historyItem = searchItem.historyItems[i]
            url = self.getHistoryItemURL(historyItem.ref)
            print "(" + str(i) + "/" + str(len(searchItem.historyItems))+ ") downloading page: " + url
            html = self.downloader.getHtml(url)
            if html == None:
                continue
            #html = self.downloader.download(url)
            historyItemParser = HistoryItemParser()
            historyItemParser.parse(html)
            tmpItem = historyItemParser.getHistoryItem()
            #historyItem.ref = tmpItem.ref
            historyItem.id = tmpItem.id
            historyItem.name = tmpItem.name
            historyItem.comments = tmpItem.comments
            historyItem.quality = tmpItem.quality
            historyItem.date = tmpItem.date
            historyItem.price = tmpItem.price
            historyItem.auctionText = tmpItem.auctionText
            historyItem.auctionData = tmpItem.auctionData
            # save the html content to tmp directory
            self.saveToTmpFile(historyItem, html)
        return

    def loadAllSearchItemsFromXml(self):
        searchResultXmlLoader = SearchResultXmlLoader()
        self.searchData = searchResultXmlLoader.loadAllXmlFiles()
        # debug
        #for searchItem in self.searchData.searchItems:
        #    self.dumpSearchItem(searchItem)
        return

    def saveAllSearchItemsToXml(self):
        for searchItem in self.searchData.searchItems:
            self.saveSearchItemToXml(searchItem)
        return

    def saveSearchItemToXml(self, searchItem):
        searchResultXmlGenerator = SearchResultXmlGenerator(searchItem)
        searchResultXmlGenerator.generateXml()
        return

    def getSearchItemByAlias(self, alias):
        if alias == None:
            return None
        for searchItem in self.searchData.searchItems:
            if cmp(searchItem.alias, alias) == 0:
                return searchItem
        return None

    def getAllSearchItems(self):
        return self.searchData.searchItems

    def saveToTmpFile(self, historyItem, html):
        fileName = 'tmp/' + historyItem.id + ".shtml"
        f= open(fileName, 'w')
        f.write(html)
        f.close()

    def saveToListFile(self, name, html):
        fileName = 'list/' + name + ".html"
        f= open(fileName, 'w')
        f.write(html)
        f.close()
        
    # debug function
    def dumpSearchItem(self, searchItem):
        print "Dumping SearchItem: " + searchItem.name
        print "  alias: " + searchItem.alias
        print "  category: " + searchItem.category
        print "  quality: " + searchItem.quality
        for historyItem in searchItem.historyItems:
            print "    name =     " + historyItem.name
            print "    comments = " + historyItem.comments

