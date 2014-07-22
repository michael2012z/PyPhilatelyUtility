# define searchCondition class
# download each search result (html) and parse
# fetch auction data
# hold auction data as tuple, id is key
# store auction data to file, load file in start


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

    def getSearchItemByAlias(self, alias):
        if alias == None:
            return None
        for searchItem in self.searchData.searchItems:
            if cmp(searchItem.alias, alias) == 0:
                return searchItem
        return None

    def getAllSearchItems(self):
        return self.searchData.searchItems

    # debug function
    def dumpSearchItem(self, searchItem):
        print "Dumping SearchItem: " + searchItem.name
        print "  alias: " + searchItem.alias
        print "  category: " + searchItem.category
        print "  quality: " + searchItem.quality
        for historyItem in searchItem.historyItems:
            print "    name =     " + historyItem.name
            print "    comments = " + historyItem.comments



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


class SearchCondition:
    base = ""
    category = ""
    quality = ""
    contains = []
    excludes = []
    folder = ""

    def SearchCondition(self, base, category, quality, contains, excludes, folder):
        self.base = base
        self.category = category
        self.quality = quality
        self.contains = contains
        self.excludes = excludes
        self.folder = folder

    def toString(self):
        return self.folder

searchConditions = [SearchCondition("", "", "", [], [], ""),
                    SearchCondition("", "", "", [], [], ""),
                    SearchCondition("", "", "", [], [], ""),
                    ]

if __name__ == '__main__':
    quitCommand = False
    while quitCommand == False:
        command = raw_input("[image downloader] ")
        parameters = command.split(' ', 4)
        if len(parameters) == 0:
            for i in len(searchConditions):
                print "" + str(i) + ". " + searchCondition.toString()
        elif parameters[0] == "q" or parameters[0] == "quit" or parameters[0] == "exit":
            quitCommand = True
        elif parameters[0] == "d" or parameters[0] == "download":
            if parameters[1] == "all":
                return
            else:
                int(parameters[1])
                
