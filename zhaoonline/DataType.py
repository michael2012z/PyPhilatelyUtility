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


categoryDic = {
    '任意' : "N",
    '清代邮票' : "140",
    '民国邮票' : "141",
    '纪特邮票' : "146",
    '文革邮票' : "171",
    '编号邮票' : "172",
    'JT邮票'   : "173",
    '散票'     : "178", 
}

qualityDic = {
    '任意' : "N",
    '全品' : "2", 
    '上品' : "3",
}

class HistoryItem():
    ref = ""
    id = ""
    name = ""
    quality = ""
    comments = ""
    date = 0
    price = 0
    auctionText = ""
    auctionData = None

class SearchItem():
    name = ""
    category = ""
    quality = ""
    historyItems = [] #HistoryItem[]

class SearchData():
    searchItems = [] #SearchItem[]
