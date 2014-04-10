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

class HistoryItemListParser(HTMLParser):
    historyItems = [] #HistoryItem[]
    html = None
    inCenterList = False
    currentPage = -1
    totalPage = 0
    itemsFoundInCurrentPage = 1

    def __init__(self):
        HTMLParser.__init__(self)
        self.historyItems = []
        self.html = None
        self.inCenterList = False
        self.currentPage = -1
        self.totalPage = 1

    def clean(self):
        self.historyItems = []
        self.html = None
        self.inCenterList = False
        self.currentPage = -1
        self.totalPage = 0
    
    def parse(self, html):
        try:
            self.itemsFoundInCurrentPage = 0
            self.feed(html)
            return True
        except Exception, e:
            print e
            return False


    def handle_starttag(self,tag,attrs):
        if self.inCenterList == True and tag == "a" and len(attrs) == 3 and attrs[2][0] == 'href':
            item = HistoryItem()
            item.ref = attrs[2][1]
            self.historyItems.append(item)
            self.itemsFoundInCurrentPage += 1 
        elif tag == "div" and len(attrs) == 2 and attrs[1] == ('id', 'center_list_id'):
            self.inCenterList = True
        elif tag == 'input' and len(attrs) == 4 and attrs[3] == ('id', 'totalPage'):
            self.totalPage = int(attrs[2][1])
        elif tag == 'input' and len(attrs) == 4 and attrs[3] == ('id', 'currentPage'):
            self.currentPage = int(attrs[2][1])

    def hasNextPage(self, page):
        return page <= self.totalPage

    def getHistoryItemList(self):
        return self.historyItems

