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


class HistoryItem():
    ref = ""
    id = ""
    name = ""
    quality = ""
    comments = ""
    date = 0
    price = 0

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
#        print "++++ handle_starttag: "
#        print tag
#        print attrs
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
#        print "++++ handle_data: "
#        print str(data)
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
                print str(data)
                self.parseAuctionData(data)
            self.parsingAuction = False


    def findBlock(self, text):
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
        print blockText[1:len(blockText)-1]
        return blockText[1:len(blockText)-1]
            

    def buildDic(self, text):
        dic = {}
        findingKey = True
        findingValue = False
        key = ""
        value = ""
        i = 0
        while(i < len(text)):
            c = text[i]
            print i
            print c
            if c == ":":
                findingKey = False
                findingValue = True
            elif c == ",":
                findingKey = True
                findingValue = False
                print "key: \n" + str(key)
                print "value: \n" + str(value)
                dic.update({key:value})
                key = ""
                value = ""
            elif c == "{" or c == "[":
                blockText = self.findBlock(text[i:])
                blockDic = self.buildDic(blockText)
                if findingValue == True:
                    value = blockDic
                else:
                    key = blockDic
                i += len(blockText) + 1
            else:
                if findingValue == True:
                    value += c
                else:
                    key += c
            i += 1
        return dic
                

    def parseAuctionData(self, auction):
        auctionText = auction
        auctionText = auctionText[str(auctionText).find('var auction'):]
        auctionText = auctionText[str(auctionText).find('{'):]
        pureAuctionText = self.findBlock(auctionText)
        dic = self.buildDic(pureAuctionText)
        print dic
        return

    def getHistoryItem(self):
        return self.historyItem





historyItemParser = HistoryItemParser()
f = open("1512865.shtml")
text = f.read()
f.close
historyItemParser.feed(text)


