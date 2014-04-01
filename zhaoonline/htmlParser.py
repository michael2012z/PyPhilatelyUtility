from HTMLParser import HTMLParser

class HtmlParser(HTMLParser):
    textttt = ""
    def __init__(self):
        HTMLParser.__init__(self)

    def handle_starttag(self,tag,attrs):
        self.textttt += "tag  : " + tag + "\n"
        self.textttt += "attrs: " + str(attrs) + "\n"
        
    def handle_data(self, data): 
        self.textttt += "data : " + data + "\n"

    def getText(self):
        return self.textttt

class HistoryItem():
    id = 0
    name = ""
    comments = ""
    quality = ""
    date = 0
    prize = 0

class HistoryItemListParser(HTMLParser):
    historyItems = [] #HistoryItem[]
    html = None
    inCenterList = False
    hasNextPage = False
    currentPage = 0
    totalPage = 0

    def __init__(self):
        HTMLParser.__init__(self)
        historyItems = []
        html = None
        inCenterList = False
        currentPage = 0
        totalPage = 0

    def clean(self):
        historyItems = []
        html = None
        inCenterList = False
        currentPage = 0
        totalPage = 0
    
    def parse(self, html):
        self.feed(html)

    def handle_starttag(self,tag,attrs):
        if self.inCenterList == True and tag == "a" and len(attrs) == 3 and attrs[2][0] == 'href':
            item = HistoryItem()
            item.ref = attrs[2][1]
            self.historyItems.append(item)
        elif tag == "div" and len(attrs) == 2 and attrs[1] == ('id', 'center_list_id'):
            self.inCenterList = True
        elif tag == 'input' and len(attrs) == 4 and attrs[3] == ('id', 'totalPage'):
            self.totalPage = int(attrs[2][1])
        elif tag == 'input' and len(attrs) == 4 and attrs[3] == ('id', 'currentPage'):
            self.currentPage = int(attrs[2][1])

    def hasNextPage(self):
        return self.currentPage < self.totalPage

    def getHistoryItemList(self):
        return self.historyItems












htmlParser = HtmlParser()
f = open("historyItem.html")
text = f.read()
f.close
htmlParser.feed(text)

f = open("historyItem.txt", "w")
f.write(htmlParser.getText())
f.close()

f = open("historyList.html")
text = f.read()
f.close
htmlParser.feed(text)

p = HistoryItemListParser()
p.parse(text)
print "current page: " + str(p.currentPage)
print "total page: " + str(p.totalPage)
b = p.hasNextPage()
print "has next page: " + str(b)
items = p.getHistoryItemList()
for item in items:
    print "ref = " + item.ref

f = open("historyList.txt", "w")
f.write(htmlParser.getText())
f.close()
