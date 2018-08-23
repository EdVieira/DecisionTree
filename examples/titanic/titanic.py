#encoding: utf-8
import tree
import datamanipulation as dml

#Open DB
print 'Opening file...'
d = open('titanic.csv', 'r')
#Make it a data matrix
print 'Converting to <list> as a data matrix'
print 'and removing lines with empty indexes...'
datamatrix = []
for i in d:
	i = i.replace('\n','')
	line = i.split('\t')
	usable = True
	for j in line:
		# checking if it has some empty data
		if len(j)<1:
			usable = False
	if usable:
		datamatrix.append(line)

#preprocess removing indexes
print 'Preprocessing...'
""" 
Columns:
PassengerId	Survived	Pclass	Name	Sex	Age	SibSp	Parch	Ticket	Fare	Cabin	Embarked
"""
useless_columns = [11,10,8,3,0] # its indexes
#useless_columns.sort()
#useless_columns.reverse()
print 'Removing indexes:', useless_columns
for i in datamatrix:
	for j in useless_columns:
		i.pop(j)

#get the tableheader
print 'Getting tableheader:'
tableheader = datamatrix.pop(0)
print tableheader
print 'Setting target index:'
target_index = tableheader.index('Survived')
print target_index

print 'Sorting data...'
datamatrix.sort()

print 'Initializing tree...'
tree = tree.Tree(tableheader, datamatrix, target_index = target_index)
print 'Show tree:'
tree.showTrees()