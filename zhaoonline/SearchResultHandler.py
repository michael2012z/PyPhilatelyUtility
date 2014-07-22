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

