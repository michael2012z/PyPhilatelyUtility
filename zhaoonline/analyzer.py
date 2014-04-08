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

class HistoryItemParser(HTMLParser):
    historyItem = None
    parsingID = False
    parsingName = False
    parsingDatePre = False
    parsingDate = False
    parsingComments = False
    parsingQuality = False
    parsingPrice = False
    parsingAuction = False

    def __init__(self):
        HTMLParser.__init__(self)
        self.historyItem = HistoryItem()

    def parse(self, html):
        self.feed(html)

    def handle_starttag(self,tag,attrs):
        if tag == "div" and len(attrs) > 0 and attrs[0] == ('class', 'Id'):
            self.parsingID = True
        elif tag == "span" and len(attrs) > 0 and attrs[0] == ('class', 'name'):
            self.parsingName = True
        elif tag == "p" and len(attrs) > 0 and attrs[0] == ('class', 'time'):
            self.parsingDatePre = True
        elif self.parsingDatePre == True and tag == "span":
            self.parsingDatePre = False
            self.parsingDate = True
        elif tag == "span" and len(attrs) > 0 and attrs[0] == ('id', 'character') and attrs[1] == ('class', 'character'):
            self.parsingQuality = True
        elif tag == "p" and len(attrs) > 0 and attrs[0] == ('class', 'currentPrice'):
            self.parsingPrice = True
        elif tag == "div" and len(attrs) > 0 and attrs[0] == ('class', 'description'):
            self.parsingComments = True
        elif tag == "script" and len(attrs) > 0 and attrs[0] == ('type', 'text/javascript'):
            self.parsingAuction = True

    def handle_data(self, data):
        if self.parsingID == True:
            self.historyItem.id = data
            self.parsingID = False
        elif self.parsingName == True:
            self.historyItem.name = data
            self.parsingName = False
        elif self.parsingDate == True:
            self.historyItem.date = data
            self.parsingDate = False
        elif self.parsingComments == True:
            self.historyItem.comments = data
            self.parsingComments = False
        elif self.parsingQuality == True:
            self.historyItem.quality = data
            self.parsingQuality = False
        elif self.parsingPrice == True:
            self.historyItem.price = data
            self.parsingPrice = False
        elif self.parsingAuction == True:
            if str(data).find('var auction') >= 0:
                (self.historyItem.auctionText, self.historyItem.auctionData) = self.parseRawAuctionData(data)
            self.parsingAuction = False


    def findAuctionBlock(self, text):
#        print "findAuctionBlock(): text = "
#        print text
        remainingBrackets = []
        blockText = ""
        for c in text:
            blockText += c
            if c == "{":
                remainingBrackets.append("}")
            elif c == "[":
                remainingBrackets.append("]")
            elif c == "]":
                if remainingBrackets[len(remainingBrackets)-1] == c:
                    del remainingBrackets[len(remainingBrackets)-1]
                    if len(remainingBrackets) == 0:
                        break
                else:
                    print "bracket [] mismatch"
                    return ""
            elif c == "}":
                if remainingBrackets[len(remainingBrackets)-1] == c:
                    del remainingBrackets[len(remainingBrackets)-1]
                    if len(remainingBrackets) == 0:
                        break
                else:
                    print "brackets {} mismatch"
                    return ""
#        print "findAuctionBlock(): return = "
#        print blockText[1:len(blockText)-1]
        return blockText[1:len(blockText)-1]
            

    def buildAuctionList(self, text):
        li = []
        i = 0
        while(i < len(text)):
            c = text[i]
            if c == "{":
                blockText = self.findAuctionBlock(text[i:])
                blockDic = self.buildAuctionDic(blockText)
                li.append(blockDic)
                i += len(blockText) + 1
            i += 1
        return li
                

    def buildAuctionDic(self, text):
        dic = {}
        findingKey = True
        findingValue = False
        key = ""
        value = ""
        i = 0
        quoting = False
        while(i < len(text)):
            c = text[i]
            if c == '"':
                if quoting == False:
                    quoting = True
                else:
                    quoting = False
            elif quoting == True:
                if findingValue == True:
                    value += c
                else:
                    key += c
            elif c == ":":
                findingKey = False
                findingValue = True
            elif c == ",":
                findingKey = True
                findingValue = False
#                print "key: \n" + str(key)
#                print "value: \n" + str(value)
                dic.update({key:value})
                key = ""
                value = ""
            elif c == "{":
                blockText = self.findAuctionBlock(text[i:])
                blockDic = self.buildAuctionDic(blockText)
                if findingValue == True:
                    value = blockDic
                else:
                    key = blockDic
                i += len(blockText) + 1
            elif c == "[":
                listText = self.findAuctionBlock(text[i:])
                blockList = self.buildAuctionList(listText)
                if findingValue == True:
                    value = blockList
                else:
                    key = blockList
                i += len(listText) + 1
            else:
                if findingValue == True:
                    value += c
                else:
                    key += c
            i += 1
        return dic

    def parseRawAuctionData(self, auction):
        auctionText = auction
        auctionText = auctionText[str(auctionText).find('var auction'):]
        auctionText = auctionText[str(auctionText).find('{'):]
        pureAuctionText = self.findAuctionBlock(auctionText)
        dic = self.buildAuctionDic(pureAuctionText)
        return (pureAuctionText, dic)

    def parsePureAuctionData(self, pureAuctionText):
        dic = self.buildAuctionDic(pureAuctionText)
        return (pureAuctionText, dic)


    def getHistoryItem(self):
        return self.historyItem


categoryDic = {
    '清代邮票' : 140,
    '民国邮票' : 141,
    '纪特邮票' : 146,
    '文革邮票' : 171,
    '编号邮票' : 172,
    'JT邮票'   : 173,
    '散票'     : 178, 
}

qualityDic = {
    '全品' : 2, 
    '上品' : 3,
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
        url += urllib.pathname2url(str(categoryDic[searchItem.category]))
        url += "-"
        url += urllib.pathname2url(str(qualityDic[searchItem.quality]))
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


class SearchResultXmlLoader():

    def __init__(self):
        return

    def loadXmlFile(self, file):
        searchItem = SearchItem()
        doc = xml.dom.minidom.parse(file)
        searchResult = doc.documentElement
        searchItem.alias = searchResult.getElementsByTagName("Alias")[0].childNodes[0].nodeValue#.encode("utf-8")
        searchItem.name = searchResult.getElementsByTagName("Keyword")[0].childNodes[0].nodeValue#.encode("utf-8")
        searchItem.category = searchResult.getElementsByTagName("Category")[0].childNodes[0].nodeValue#.encode("utf-8")
        searchItem.quality = searchResult.getElementsByTagName("Quality")[0].childNodes[0].nodeValue#.encode("utf-8")
        items = searchResult.getElementsByTagName("ItemList")[0].childNodes
        for item in items:
            print item
            try:
                historyItem = HistoryItem()
                historyItem.ref = item.getElementsByTagName("Ref")[0].childNodes[0].nodeValue#.encode("utf-8")
                #print historyItem.ref
                historyItem.id = item.getElementsByTagName("ID")[0].childNodes[0].nodeValue#.encode("utf-8")
                #print historyItem.id
                historyItem.name = item.getElementsByTagName("Name")[0].childNodes[0].nodeValue#.encode("utf-8")
                #print historyItem.name
                historyItem.quality = item.getElementsByTagName("Quality")[0].childNodes[0].nodeValue#.encode("utf-8")
                #print historyItem.quality
                historyItem.comments = item.getElementsByTagName("Comments")[0].childNodes[0].nodeValue#.encode("utf-8")
                #print historyItem.comments
                historyItem.date = item.getElementsByTagName("Date")[0].childNodes[0].nodeValue#.encode("utf-8")
                #print historyItem.date
                historyItem.price = item.getElementsByTagName("Price")[0].childNodes[0].nodeValue#.encode("utf-8")
                #print historyItem.price
                historyItem.auctionText = item.getElementsByTagName("Auction")[0].childNodes[0].nodeValue#.encode("utf-8")
                #print historyItem.auctionText
                #historyItemParser = HistoryItemParser()
                #(xxx, historyItem.auctionData) = historyItemParser.parsePureAuctionData(historyItem.auctionText)

                searchItem.historyItems.append(historyItem)
            except Exception, e:
                #print e
                continue

        return searchItem

    def loadAllXmlFiles(self):
        searchData = SearchData()
        fileNames = os.listdir('data/')
        for fileName in fileNames:
            fileName = 'data/' + fileName
            if os.path.isfile(fileName):
                fileNameBase, fileNameExt = os.path.splitext(fileName)
                if cmp(fileNameExt, '.xml') == 0:
                    print "loading file: " + fileName
                    searchItem = self.loadXmlFile(fileName)
                    searchData.searchItems.append(searchItem)
        return searchData


class SearchResultXmlGenerator():
    dom = None
    root = None
    itemList = None
    searchItem = None

    def __init__(self, searchItem):
        self.searchItem = searchItem
        impl = xml.dom.minidom.getDOMImplementation()
        self.dom = impl.createDocument(None, 'SearchResult', None)
        self.root = self.dom.documentElement 
        return
        
    def setAlias(self, aliasText):
        alias = self.dom.createElement('Alias')
        aliasValue = self.dom.createTextNode(aliasText)
        alias.appendChild(aliasValue)
        self.root.appendChild(alias)

    def setKeyword(self, keywordText):
        keyword = self.dom.createElement('Keyword')
        keywordValue = self.dom.createTextNode(keywordText)
        keyword.appendChild(keywordValue)
        self.root.appendChild(keyword)

    def setCategory(self, categoryText):
        category = self.dom.createElement('Category')
        categoryValue = self.dom.createTextNode(categoryText)
        category.appendChild(categoryValue)
        self.root.appendChild(category)

    def setQuality(self, qualityText):
        quality = self.dom.createElement('Quality')
        qualityValue = self.dom.createTextNode(qualityText)
        quality.appendChild(qualityValue)
        self.root.appendChild(quality)

    def addHistoryItem(self, historyItem):
        item = self.dom.createElement('Item')

        tag = self.dom.createElement('Ref')
        value = self.dom.createTextNode(historyItem.ref)
        tag.appendChild(value)
        item.appendChild(tag)

        tag = self.dom.createElement('ID')
        value = self.dom.createTextNode(historyItem.id)
        tag.appendChild(value)
        item.appendChild(tag)

        tag = self.dom.createElement('Name')
        value = self.dom.createTextNode(historyItem.name)
        tag.appendChild(value)
        item.appendChild(tag)

        tag = self.dom.createElement('Quality')
        value = self.dom.createTextNode(historyItem.quality)
        tag.appendChild(value)
        item.appendChild(tag)

        tag = self.dom.createElement('Comments')
        value = self.dom.createTextNode(historyItem.comments)
        tag.appendChild(value)
        item.appendChild(tag)

        tag = self.dom.createElement('Date')
        value = self.dom.createTextNode(str(historyItem.date))
        tag.appendChild(value)
        item.appendChild(tag)

        tag = self.dom.createElement('Price')
        value = self.dom.createTextNode(str(historyItem.price))
        tag.appendChild(value)
        item.appendChild(tag)

        tag = self.dom.createElement('Auction')
        value = self.dom.createTextNode(str(historyItem.auctionText))
        tag.appendChild(value)
        item.appendChild(tag)

        if self.itemList == None:
            self.itemList = self.dom.createElement('ItemList')
            self.root.appendChild(self.itemList)
        self.itemList.appendChild(item)

    def writeToFile(self):
        f= open("data/" + self.searchItem.name + "_" + self.searchItem.category + "_" + self.searchItem.quality + ".xml", 'w')
        self.dom.writexml(f, addindent='  ', newl='\n',encoding='utf-8')
        f.close() 

    def generateXml(self):
        self.setAlias(self.searchItem.alias)
        self.setKeyword(self.searchItem.name)
        self.setCategory(self.searchItem.category)
        self.setQuality(self.searchItem.quality)
#.decode("utf-8").encode("GBK"))
#.decode("GBK").encode("utf-8"))
        for item in self.searchItem.historyItems:
            self.addHistoryItem(item)
        self.writeToFile()



class TestHistoryItemParser(HTMLParser):
    text = ""
    def __init__(self):
        HTMLParser.__init__(self)

    def parse(self, html):
        self.feed(html)

    def handle_starttag(self,tag,attrs):
        self.text += "tag   : " + tag + "\n"
        self.text += "attrs : " + str(attrs) + "\n"
        
    def handle_data(self, data):
        self.text += "data  : " + str(data) + "\n"
        
    def getText(self):
        return self.text

import random

def ttt():
    x = []
    y = []
    for i in range(0, 5):
        x.append(date.fromordinal(730920 + random.randint(0, 10)))
        y.append(random.randint(10, 20))
    print x
    print y
    plt.plot(x, y)
    plt.title('Title')
    plt.ylabel('Price')
    plt.xlabel('Date')
    plt.grid(True)
    #fig = plt.figure()
    #fig.autofmt_xdate()
    plt.show()

def encodingTest():
    h = '汉字'
    u = u'汉字'
    i = raw_input()
    print h, h.decode("utf-8"), h.decode("utf-8").encode("GBK")
    print u
    print i

    print urllib.pathname2url(h)
    print urllib.pathname2url(u.encode("utf-8"))
    print urllib.pathname2url(i.decode("gbk").encode("utf-8"))
    return

if __name__ == '__main__':
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
                if cmp(category, '清代邮票') != 0 and cmp(category, '民国邮票') != 0 and cmp(category, '散票') != 0 and cmp(category, '纪特邮票') != 0 and cmp(category, '文革邮票') != 0 and cmp(category, '编号邮票') != 0 and cmp(category, 'JT邮票') != 0:
                    print "ERROR: unknown category type: " + category
                elif cmp(quality, '全品') != 0 and cmp(quality, '上品') != 0:
                    print "ERROR: unknown quality type: " + quality
                else:
                    newSearchItem = dataHandler.addSearchItem(alias, name, category, quality)
                return

            # format: add <alias> <name> <category> <quality>
            if len(parameters) == 5:
                add(parameters)
            elif len(parameters) == 2 and parameters[1] == "all":
                f = open("addAll.txt")
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
                    print "ERROR: offline mode, can't update"
                    continue
                alias = parameters[1]
                searchItem = dataHandler.getSearchItemByAlias(alias)
                if searchItem == None:
                    print "ERROR: can't find alias: " + alias
                else:
                    historyItems = sorted(searchItem.historyItems, key=lambda x: x.date)
                    downloadList = []
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
                                    picFileName = "image/" + picURL.split("/")[-1]
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


