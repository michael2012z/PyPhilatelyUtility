import xml.dom.minidom

def generateXML():
    impl = xml.dom.minidom.getDOMImplementation()
    dom = impl.createDocument(None, 'SearchResult', None)
    root = dom.documentElement 

    keyword = dom.createElement('Keyword')
    keywordValue = dom.createTextNode('xxxxx')
    keyword.appendChild(keywordValue)
    root.appendChild(keyword)

    category = dom.createElement('Category')
    categoryValue = dom.createTextNode('Categoryxxxxx')
    category.appendChild(categoryValue)
    root.appendChild(category)

    itemList = dom.createElement('ItemList')
    root.appendChild(itemList)

    item = dom.createElement('Item')
    id = dom.createElement('ID')
    idValue = dom.createTextNode('Idxxxxx')
    id.appendChild(idValue)
    item.appendChild(id)
    name = dom.createElement('Name')
    nameValue = dom.createTextNode('Namexxxxx')
    name.appendChild(nameValue)
    item.appendChild(name)
    itemList.appendChild(item)

    item = dom.createElement('Item')
    id = dom.createElement('ID')
    idValue = dom.createTextNode('Idyyyyy')
    id.appendChild(idValue)
    item.appendChild(id)
    name = dom.createElement('Name')
    nameValue = dom.createTextNode('Nameyyyyy')
    name.appendChild(nameValue)
    item.appendChild(name)
    itemList.appendChild(item)

    f= open('test.xml', 'w')
    dom.writexml(f, addindent='  ', newl='\n',encoding='utf-8')
    f.close()  

generateXML()
