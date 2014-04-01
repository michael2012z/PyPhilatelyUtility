# -*- coding: utf-8 -*-

h = '汉字'
u = u'汉字'
i = raw_input()
print h, h.decode("utf-8"), h.decode("utf-8").encode("GBK")
print u
print i

print i==h


