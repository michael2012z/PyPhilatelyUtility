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


class HtmlDownloader():
    offLine = False
    headers = {'Host': 'www.zhaoonline.com',
               'Connection': 'keep-alive',
               'Content-Length': '50',
               'Accept': '*/*',
               'Origin': 'www.zhaoonline.com',
               'X-Requested-With': 'XMLHttpRequest',
               'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31',
               'Content-Type': 'application/x-www-form-urlencoded',
               'Referer': 'http://www.zhaoonline.com/',
               #'Accept-Encoding': 'gzip,deflate,sdch',
               #'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'
               'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4'}
    login_data = None

    def __init__(self, user, passwd):
        # initialize the opener, cookie
        if user != None and passwd != None:
            self.login_data = urllib.urlencode({'loginId': user, 'password': passwd, 'back': 'index'})
        else:
            # offline mode
            self.offLine = True
            print "Warning: username/passwd not provided, working in offline mode"
            return

        try:
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            urllib2.install_opener(opener)
            host_url = r'http://www.zhaoonline.com/'
            login_url = r'http://www.zhaoonline.com/login/submit.shtml'
            h = urllib2.urlopen(host_url)
            request = urllib2.Request(login_url, self.login_data, self.headers)
            response = urllib2.urlopen(request)  
            response.read()
        except Exception, e:
            self.offLine = True
            print "Warning: network not available, working in offline mode"

    def isOffLine(self):
        return self.offLine

    def getHtml(self, url):
        #print "downloading file: " + url
        request = urllib2.Request(url, self.login_data, self.headers)
        try:
            response = urllib2.urlopen(request)  
            html = response.read()
        except Exception, e:
            html = None
        return html
    
    def downLoad(self, url):
        #print "downloading file: " + url
        request = urllib2.Request(url, self.login_data, self.headers)
        try:
            response = urllib2.urlopen(request)  
            downloaded = response.read()
        except Exception, e:
            print e
            downloaded = None
        return downloaded

