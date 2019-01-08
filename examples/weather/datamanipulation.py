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

# encoding: utf-8

def vector_get_distinct(v):
	res = []
	for i in v:
		if not (i in res):
			res.append(i)
	return res


def list_get_column(mt, index):
	# :list
	#get a column from a matrix
	res = []
	for i in mt:
		res.append(i[index])
		#for j in i:
		#	if i.index(j) == index:
		#		res.append(j)
		#		break
	return res

def list_get_column_distinct(mt, index):
	# :list
	#get distinct values of a column
	res = []
	col = list_get_column(mt,index)
	res = vector_get_distinct(col)
	return res

def list_get_where(mt, column, value, relation = '=='):
	# :list
	#get distinct values of a column

	res = []
	for i in mt:
		n = i[column]
		if isnumeric(n) and isnumeric(value):
			n = float(n)
			value = float(value)
		s = 'value '+ relation
		if relation != '==':
			s = 'not ' + s +' n'
		else:
			s = s +' n'
		if eval(s):
			res.append(i)
	return res

def list_get_distincts(matrix, tableheader, exceptColumns = []):
	# :json
	#get distinct values from each column of a matrix as a json
	distinctis = []
	for i in range(len(tableheader)):
		# get distinct value of each row
		distinctis.append(get_column_distinct(matrix,i))
	distinctis = listToJson(distinctis)
	for i in range(len(distinctis)):
		# attach each distinct as key value
		if not tableheader[i] in exceptColumns:
			distinctis[tableheader[i]] = distinctis[i]
			del distinctis[i]
			# from this -> {'play': {0: 'yes', 1: 'no'}, 'temperature': {0: 'cool', 1: 'hot', 2: 'mild'}, 'outlook': {0: 'overcast', 1: 'rainy', 2: 'sunny'}, 'humidity': {0: 'normal', 1: 'high'}, 'windy': {0: 'TRUE', 1: 'FALSE'}}
			for j in range(len(distinctis[tableheader[i]])):
				# attach each distinct value of key value as its branch names
				distinctis[tableheader[i]][distinctis[tableheader[i]][j]] = []
				del distinctis[tableheader[i]][j]
				# to this -> {'play': {'yes': [], 'no': []}, 'temperature': {'mild': [], 'hot': [], 'cool': []}, 'outlook': {'overcast': [], 'sunny': [], 'rainy': []}, 'humidity': {'high': [], 'normal': []}, 'windy': {'TRUE': [], 'FALSE': []}}
		else:
			del distinctis[i]
	return distinctis

def listToJson(l):
	# :json
	# convert list to json keeping its positions
	data = {}
	for i in range(len(l)):
		data[i] = {}
		if type(l[i]) == type([]):
			data[i] = listToJson(l[i])
		else:
			data[i]= l[i]
	return data

def applyKeys(js, tableheader):
	# :json
	# attach the name of the column to its position
	for i in js:
		for j in range(len(js[i])):
			js[i][tableheader[j]] = js[i][j]
			del js[i][j]
	return js

def searchJSONwhereLike(js, key, value, relation = 'in'):
	res = {}
	for i in js:
		s = 'value '+relation+' js[i][key]'
		if eval(s):
			res[len(res)] = js[i]
	return res

def isnumeric(v):
	# It checks if list elements are numeric data
	try:
		t = float(v)
		return True
	except Exception as e:
		return False

def list_isnumeric(l):
	# It checks if list elements are numeric data
	res = False
	for i in l:
		res = isnumeric(i)
		if res:
			break
	return res

"""
datamatrix.sort()
for i in datamatrix:
	print i
print '|||||'

# converts list to json
jdata = listToJson(datamatrix)

# attach its keys
jdata = applyKeys(jdata, tableheader)

#print jdata

print "|||| distincts from data"
# get distincts values from each column
dstOutlook = get_distincts(datamatrix,tableheader)
print dstOutlook

#print "|||| distincts exceptColumns ['outlook', 'play']"
# get distincts values from each column
#dst = get_distincts(datamatrix,tableheader, exceptColumns = ['outlook', 'play'])
#print dst

print "||||"
# search JSON where attribute 'outlook' like 'sunny'
p = searchJSONwhereLike(jdata, 'outlook', 'overcast')
q = searchJSONwhereLike(p, 'play', 'yes')
print len(p)
print len(q)

#def filterByKey(js, keySource, svalue, keyFilter, filterValue):
#	p = searchJSONwhereLike(jdata, keySource, svalue)
#	q = searchJSONwhereLike(p, keyFilter, filterValue)
#	#return len(p), len(q)
#	return q

#print p==filterByKey(jdata,'outlook','overcast','play','yes')
target = 'play'
targetValues = ['yes','no']
for i in dstOutlook:
	if not i == target:
		for j in dstOutlook[i]:
			print i
			print j
			print dstOutlook[i]
			print dstOutlook[i][j]
			for t in targetValues:
				res = searchJSONwhereLike(jdata, target, t)
				res = searchJSONwhereLike(res, i, j)
				if len(res) > 0:
					dstOutlook[i][j].append(res)
print '||||||||'
for i in dstOutlook:
	print i
	for j in dstOutlook[i]:
		print j
		print len(dstOutlook[i][j])
"""