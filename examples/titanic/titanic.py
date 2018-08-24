"""
The MIT License (MIT)
Copyright (c) 2017 Eduardo Henrique Vieira dos Santos
Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
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