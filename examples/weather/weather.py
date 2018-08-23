#encoding: UTF-8
import tree
import datamanipulation as dml

# Table header
tableheader = ['outlook', 'temperature', 'humidity', 'windy', 'play']

# Data Matrix
"""
datamatrix = [
	['sunny','hot','high','FALSE','no'],
	['sunny','hot','high','TRUE','no'],
	['overcast','hot','high','FALSE','yes'],
	['rainy','mild','high','FALSE','yes'],
	['rainy','cool','normal','FALSE','yes'],
	['rainy','cool','normal','TRUE','no'],
	['overcast','cool','normal','TRUE','yes'],
	['sunny','mild','high','FALSE','no'],
	['sunny','cool','normal','FALSE','yes'],
	['rainy','mild','normal','FALSE','yes'],
	['sunny','mild','normal','TRUE','yes'],
	['overcast','mild','high','TRUE','yes'],
	['overcast','hot','normal','FALSE','yes'],
	['rainy','mild','high','TRUE','no']
]
"""
datamatrix = [
	['sunny','hot','high','FALSE',25],
	['sunny','hot','high','TRUE',30],
	['overcast','hot','high','FALSE',46],
	['rainy','mild','high','FALSE',45],
	['rainy','cool','normal','FALSE',52],
	['rainy','cool','normal','TRUE',23],
	['overcast','cool','normal','TRUE',43],
	['sunny','mild','high','FALSE',35],
	['sunny','cool','normal','FALSE',35],
	['rainy','mild','normal','FALSE',38],
	['sunny','mild','normal','TRUE',46],
	['overcast','mild','high','TRUE',48],
	['overcast','hot','normal','FALSE',52],
	['rainy','mild','high','TRUE',44]
]
"""
datamatrix = [
	['sunny','33','high','FALSE',25],
	['sunny','32','high','TRUE',30],
	['overcast','31','high','FALSE',46],
	['rainy','22','high','FALSE',45],
	['rainy','13','normal','FALSE',52],
	['rainy','15','normal','TRUE',23],
	['overcast','12','normal','TRUE',43],
	['sunny','25','high','FALSE',35],
	['sunny','13','normal','FALSE',35],
	['rainy','23','normal','FALSE',38],
	['sunny','24','normal','TRUE',46],
	['overcast','25','high','TRUE',48],
	['overcast','24','normal','FALSE',52],
	['rainy','21','high','TRUE',44]
]
"""
"""
datamatrix = [
	['1','33','90','0',25],
	['1','32','90','1',30],
	['50','31','90','0',46],
	['100','22','90','0',45],
	['100','13','50','0',52],
	['100','15','50','1',23],
	['50','12','50','1',43],
	['1','25','90','0',35],
	['1','13','50','0',35],
	['100','23','50','0',38],
	['1','24','50','1',46],
	['50','25','90','1',48],
	['50','24','50','0',52],
	['100','21','90','1',44]
]
"""
datamatrix.sort()
tree = tree.Tree(tableheader, datamatrix)#, mode="between")
tree.showTrees()
print 'PREDICTION'
#tree.predict(['sunny','hot','high','FALSE'])
tree.predict(['sunny','hot','high','FALSE'])
#tree.predict(['sunny','33','high','FALSE'])
#print tree.predict(['1','24','50','1'])