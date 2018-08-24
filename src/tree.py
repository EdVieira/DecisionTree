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

import datamanipulation as dml
import math
from decimal import Decimal



def isnumeric(v):
	# It checks if list elements are numeric data
	try:
		t = Decimal(v)
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

class Tree(object):
	"""docstring for Tree"""
	def __init__(self, tableheader, datamatrix, mode = 'avg', target_index = None):
		super(Tree, self).__init__()
		self.tableheader = tableheader
		self.datamatrix = datamatrix
		self.target_index = 0
		if target_index == None:
			self.target_index = len(tableheader)-1
		else:
			self.target_index = target_index
		self.root = None
		self.nodes = []
		self.std_cv = 15 # Coefficient of Deviation (CV) is used to decide when to stop branching. We can use Count (n) as well.
		self.mode = mode # 'avg', 'between'
		self.mountNodesAndBranches(self.tableheader, self.datamatrix)

	def showTrees(self):
		print 'TREE_MIN_DEPTH:',self.root.countMinLevel()
		print '\nTREE_INDEX',self.root
		self.root.showTree()

	def predict(self, vector):
		return self.root.predict(vector = vector)

	def mountNodesAndBranches(self, tableheader, datamatrix, rootBranch = None, level = 0):
		datamatrix.sort()
		if rootBranch != None:
			nodes = []
			# ADD remaining nodes (related to the column label)
			for i in range(len(tableheader)):
				# table index
				tindex = self.tableheader.index(tableheader[i])
				if tindex != self.target_index:
					# if its not the target index
					if tableheader[i] not in rootBranch.get_root_labels():
						# if column label wasnt noded by its parents yet
						n = Node(tree = self, label = tableheader[i], index = tindex, rootBranch = rootBranch,level = level)
						nodes.append(n)
			#print "LEVEL",level, tableheader

			# Check branch possibility for each node
			for i in nodes:
				#print 'node: ',i.label
				# Get distinct values from this node corresponding column
				#if len(i.get_root_data()) < 1:
				#	nodes.remove(i)
				#	continue
				column_values = dml.list_get_column(datamatrix, i.index)
				# Check if the values from the column of this node are numeric
				if not list_isnumeric(column_values):
					# If it is NOT numeric
					distincts = dml.vector_get_distinct(column_values)
					# Add a branch for each distinct value
					for j in range(len(distincts)):
						if distincts[j] not in i.get_root_labels():
							t = Branch(rootNode = i, value = distincts[j])
							i.branches.append(t)

					# Check branching possibility for each Branch added to this node
					for branch in i.branches:
						# Get its filtered matrix
						branchMatrix = branch.get_models()
						#if len(branchMatrix) < 1:
							#i.branches.remove(branch)
							#continue
						#print i.label
						#print '___',branch.relation,branch.value
						#print '____|____',branchMatrix
						# Get the distinct values from target column
						res = dml.list_get_column(branchMatrix, self.target_index)
						rescopy = []
						rescopy.extend(res)

						# MEASURE TARGET COLUMN STANDARD DEVIATION and its coefficient
						# Statistics variable
						isn = True
						n = 1 #  Count Elements.
						avg = 1 # Average (Avg) is the value in the leaf nodes(branch value).
						std_dev = 1 # Standard Deviation (S) is for tree building (branching)
						cv = 0 # Coefficient of Deviation (CV) is used to decide when to stop branching. We can use Count (n) as well.

						# Check if target index is not numeric and prepare the data
						if not list_isnumeric(rescopy):
							isn = False
							rescopy = dml.vector_get_distinct(rescopy)
							for index in range(len(rescopy)):
								rescopy[index] = index+1
						else:
							for index in range(len(rescopy)):
								rescopy[index] = Decimal(rescopy[index])

						# Measure statistics
						n = len(rescopy) # the set length
						#print i.label
						#print 'branch: ',branch.value
						#print rescopy
						avg = Decimal(sum(rescopy))/Decimal(n) # the set mean
						#print avg
						aux = Decimal(0.0)
						for s in rescopy:
							aux = aux + (s - avg)**2
						std_dev = Decimal(math.sqrt(aux/n)) # the set standard deviation
						#print std_dev
						if std_dev != avg:
							cv = std_dev/avg*100 # the set coeficient of deviation
						else:
							cv = 0

						# check standard cv trigger to stop or keep branching
						if cv > self.std_cv and len(tableheader)>2:
							# keep recursive branching
							#print i.label, branch.relation, branch.value
							th = []
							th.extend(tableheader)
							th.remove(i.label)
							branch.nodes = self.mountNodesAndBranches(th, branchMatrix, rootBranch = branch,level = level+1)
						else:
							# stop recursive branching and add leaf node to last branch
							#print i.label, branch.relation, branch.value
							n = Node(tree = self, label = self.tableheader[self.target_index], index = self.target_index, rootBranch = branch,level = level+1)
							nb = None
							if isn:
								#print avg, res[0]
								if self.mode == 'avg':
									nb = Branch(rootNode = n, value = avg, relation = '==', std_dev = std_dev)
									n.branches.append(nb)
								elif self.mode == 'between':
									res.sort()
									nb1 = Branch(rootNode = n, value = res[0], relation = '>=', std_dev = std_dev)
									n.branches.append(nb1)
									nb2 = Branch(rootNode = n, value = res[-1], relation = '<=', std_dev = std_dev)
									n.branches.append(nb2)
							else:
								#print avg, res[0]
								nb = Branch(rootNode = n, value = res[0], std_dev = std_dev)
								n.branches.append(nb)
							branch.nodes.append(n)
						#print i.label, branch.relation, branch.value
				else:
					# If it IS numeric
					column_values = dml.list_get_column(i.get_root_data(), i.index)
					n = 1.0 #  Count Elements.
					avg = 1.0 # Average (Avg) is the value in the leaf nodes(branch value).
					n = len(column_values) # the set length
					for j in range(len(column_values)):
						column_values[j] = Decimal(column_values[j])
					avg = Decimal(sum(column_values))/Decimal(n) # the set mean
					distincts = dml.vector_get_distinct(column_values)
					if len(distincts) > 1:
						distincts = ['<=','>']
					else:
						# verify if its above or under the global mean
						cval = dml.list_get_column(self.datamatrix, i.index)
						for j in range(len(cval)):
							cval[j] = Decimal(cval[j])
						cval_avg = sum(cval)/len(cval)
						if avg > cval_avg:
							distincts = ['>=']
							avg = avg - Decimal(0.0001)
						else:
							avg = avg + Decimal(0.0001)
							distincts = ['<=']
					# Add a branch for each distinct value
					for j in range(len(distincts)):
						#print i.label, avg
						t = Branch(rootNode = i, value = avg, relation = distincts[j])
						i.branches.append(t)

					# Check branching possibility for each Branch added to this node
					for branch in i.branches:
						# Get its filtered matrix
						branchMatrix = branch.get_models()
						#if len(branchMatrix) < 1:
						#	i.branches.remove(branch)
						#	continue
						#print i.label
						#print '___',branch.relation,branch.value
						#print '____|____',branchMatrix
						# Get the distinct values from target column
						res = dml.list_get_column(branchMatrix, self.target_index)
						rescopy = []
						rescopy.extend(res)

						# MEASURE TARGET COLUMN STANDARD DEVIATION and its coefficient
						# Statistics variable
						isn = True
						n = 1 #  Count Elements.
						avg = 1 # Average (Avg) is the value in the leaf nodes(branch value).
						std_dev = 1 # Standard Deviation (S) is for tree building (branching)
						cv = 0 # Coefficient of Deviation (CV) is used to decide when to stop branching. We can use Count (n) as well.

						# Check if target index is not numeric and prepare the data
						if not list_isnumeric(rescopy):
							isn = False
							rescopy = dml.vector_get_distinct(rescopy)
							for index in range(len(rescopy)):
								rescopy[index] = index+1
						else:
							for index in range(len(rescopy)):
								rescopy[index] = Decimal(rescopy[index])
						# Measure statistics
						n = len(rescopy) # the set length
						if n == 0:
							#print 'branch',branch.value
							break
						for j in range(len(rescopy)):
							rescopy[j] = Decimal(rescopy[j])
						avg = Decimal(sum(rescopy))/Decimal(n) # the set mean
						aux = Decimal(0.0)
						for s in rescopy:
							aux = aux + (s - avg)**2
						std_dev = Decimal(math.sqrt(aux/n)) # the set standard deviation
						if std_dev != avg:
							cv = std_dev/avg*100 # the set coeficient of deviation
						else:
							cv = 0

						# check standard cv trigger to stop or keep branching
						if cv > self.std_cv and len(tableheader)>2:
							# keep recursive branching
							#print i.label, branch.relation, branch.value
							th = []
							th.extend(tableheader)
							th.remove(i.label)
							branch.nodes = self.mountNodesAndBranches(th, branchMatrix, rootBranch = branch,level = level+1)
						else:
							# stop recursive branching and add leaf node to last branch
							n = Node(tree = self, label = self.tableheader[self.target_index], index = self.target_index, rootBranch = branch,level = level+1)
							nb = None
							if isn:
								#print avg, res[0]
								if self.mode == 'avg':
									nb = Branch(rootNode = n, value = avg, relation = '==', std_dev = std_dev)
									n.branches.append(nb)
								elif self.mode == 'between':
									res.sort()
									nb1 = Branch(rootNode = n, value = res[0], relation = '>=', std_dev = std_dev)
									n.branches.append(nb1)
									nb2 = Branch(rootNode = n, value = res[-1], relation = '<=', std_dev = std_dev)
									n.branches.append(nb2)
							else:
								#print avg, res[0]
								nb = Branch(rootNode = n, value = res[0], std_dev = std_dev)
								n.branches.append(nb)
							branch.nodes.append(n)
						#print i.label, branch.relation, branch.value
			self.nodes = nodes
		if rootBranch == None:

			nodes = []
			for i in range(len(tableheader)):
				tindex = self.tableheader.index(tableheader[i])
				if rootBranch != None and  tindex != self.target_index:
					if tableheader[i] not in rootBranch.get_root_labels():
						n = Node(tree = self, label = tableheader[i], index = tindex, rootBranch = rootBranch,level = level)
						nodes.append(n)
				elif tindex != self.target_index:
					n = Node(tree = self, label = tableheader[i], index = tindex, rootBranch = rootBranch,level = level)
					nodes.append(n)

			#print "LEVEL",level
			for i in nodes:
				# Get distinct values from this node corresponding column
				#if len(i.get_root_data()) < 1:
				#	nodes.remove(i)
				#	continue
				column_values = dml.list_get_column(datamatrix, i.index)
				# Check if the values from the column of this node are numeric
				if not list_isnumeric(column_values):
					#print column_values
					#print "not numeric"
					# If it is NOT numeric
					distincts = dml.vector_get_distinct(column_values)
					# Add a branch for each distinct value
					for j in range(len(distincts)):
						if distincts[j] not in i.get_root_labels():
							t = Branch(rootNode = i, value = distincts[j])
							i.branches.append(t)

					# Check branching possibility for each Branch added to this node
					for branch in i.branches:
						# Get its filtered matrix
						branchMatrix = branch.get_models()
						#if len(branchMatrix) < 1:
						#	i.branches.remove(branch)
						#	continue
						#print i.label
						#print '___',branch.relation,branch.value
						#print '____|____',branchMatrix
						# Get the distinct values from target column
						res = dml.list_get_column(branchMatrix, self.target_index)
						rescopy = []
						rescopy.extend(res)

						# MEASURE TARGET COLUMN STANDARD DEVIATION and its coefficient
						# Statistics variable
						isn = True
						n = 1 #  Count Elements.
						avg = 1 # Average (Avg) is the value in the leaf nodes(branch value).
						std_dev = 1 # Standard Deviation (S) is for tree building (branching)
						cv = 0 # Coefficient of Deviation (CV) is used to decide when to stop branching. We can use Count (n) as well.

						# Check if target index is not numeric and prepare the data
						if not list_isnumeric(rescopy):
							isn = False
							rescopy = dml.vector_get_distinct(rescopy)
							for index in range(len(rescopy)):
								rescopy[index] = index+1
						else:
							for index in range(len(rescopy)):
								rescopy[index] = Decimal(rescopy[index])

						# Measure statistics
						n = len(rescopy) # the set length
						#print 'branch: ',branch.value
						avg = Decimal(sum(rescopy))/Decimal(n) # the set mean
						aux = Decimal(0.0)
						for s in rescopy:
							aux = aux + (s - avg)**2
						std_dev = Decimal(math.sqrt(aux/n)) # the set standard deviation
						if std_dev != avg:
							cv = std_dev/avg*100 # the set coeficient of deviation
						else:
							cv = 0

						# check standard cv trigger to stop or keep branching
						if cv > self.std_cv and len(tableheader)>2:
							# keep recursive branching
							th = []
							th.extend(tableheader)
							th.remove(i.label)
							branch.nodes = self.mountNodesAndBranches(th, branchMatrix, rootBranch = branch,level = level+1)
						else:
							# stop recursive branching and add leaf node to last branch
							#print i.label, branch.relation, branch.value
							n = Node(tree = self, label = self.tableheader[self.target_index], index = self.target_index, rootBranch = branch,level = level+1)
							nb = None
							if isn:
								#print avg, res[0]
								if self.mode == 'avg':
									nb = Branch(rootNode = n, value = avg, relation = '==', std_dev = std_dev)
									n.branches.append(nb)
								elif self.mode == 'between':
									res.sort()
									nb1 = Branch(rootNode = n, value = res[0], relation = '>=', std_dev = std_dev)
									n.branches.append(nb1)
									nb2 = Branch(rootNode = n, value = res[-1], relation = '<=', std_dev = std_dev)
									n.branches.append(nb2)
							else:
								#print avg, res[0]
								nb = Branch(rootNode = n, value = res[0], std_dev = std_dev)
								n.branches.append(nb)
							branch.nodes.append(n)
						#print i.label, branch.relation, branch.value
				else:
					# If it IS numeric
					column_values = dml.list_get_column(i.get_root_data(), i.index)
					n = 1.0 #  Count Elements.
					avg = 1.0 # Average (Avg) is the value in the leaf nodes(branch value).
					n = len(column_values) # the set length
					for j in range(len(column_values)):
						column_values[j] = Decimal(column_values[j])
					avg = Decimal(sum(column_values))/Decimal(n) # the set mean
					distincts = dml.vector_get_distinct(column_values)
					if len(distincts) > 1:
						distincts = ['<=','>']
					else:
						# verify if its above or under the global mean
						cval = dml.list_get_column(self.datamatrix, i.index)
						for j in range(len(cval)):
							cval[j] = Decimal(cval[j])
						cval_avg = sum(cval)/len(cval)
						if avg > cval_avg:
							distincts = ['>=']
						else:
							distincts = ['<=']
					# Add a branch for each distinct value
					for j in range(len(distincts)):
						t = Branch(rootNode = i, value = avg, relation = distincts[j])
						i.branches.append(t)

					# Check branching possibility for each Branch added to this node
					for branch in i.branches:
						# Get its filtered matrix
						branchMatrix = branch.get_models()
						#if len(branchMatrix) < 1:
						#	i.branches.remove(branch)
						#	continue
						#print i.label
						#print '___',branch.relation,branch.value
						#print '____|____',branchMatrix
						# Get the distinct values from target column
						res = dml.list_get_column(branchMatrix, self.target_index)
						rescopy = []
						rescopy.extend(res)

						# MEASURE TARGET COLUMN STANDARD DEVIATION and its coefficient
						# Statistics variable
						isn = True
						n = 1 #  Count Elements.
						avg = 1 # Average (Avg) is the value in the leaf nodes(branch value).
						std_dev = 1 # Standard Deviation (S) is for tree building (branching)
						cv = 0 # Coefficient of Deviation (CV) is used to decide when to stop branching. We can use Count (n) as well.

						# Check if target index is not numeric and prepare the data
						if not list_isnumeric(rescopy):
							isn = False
							rescopy = dml.vector_get_distinct(rescopy)
							for index in range(len(rescopy)):
								rescopy[index] = index+1
						else:
							for index in range(len(rescopy)):
								rescopy[index] = Decimal(rescopy[index])

						# Measure statistics
						n = len(rescopy) # the set length
						if n < 1:
							#print 'branch',branch.value
							break
						for j in range(len(rescopy)):
							rescopy[j] = Decimal(rescopy[j])
						avg = Decimal(sum(rescopy))/Decimal(n) # the set mean
						aux = Decimal(0.0)
						for s in rescopy:
							aux = aux + (s - avg)**2
						std_dev = Decimal(math.sqrt(aux/n)) # the set standard deviation
						if std_dev != avg:
							cv = std_dev/avg*100 # the set coeficient of deviation
						else:
							cv = 0

						# check standard cv trigger to stop or keep branching
						if cv > self.std_cv and len(tableheader)>2:
							# keep recursive branching
							#print i.label, branch.relation, branch.value
							th = []
							th.extend(tableheader)
							th.remove(i.label)
							branch.nodes = self.mountNodesAndBranches(th, branchMatrix, rootBranch = branch,level = level+1)
						else:
							# stop recursive branching and add leaf node to last branch
							n = Node(tree = self, label = self.tableheader[self.target_index], index = self.target_index, rootBranch = branch,level = level+1)
							nb = None
							if isn:
								#print avg, res[0]
								if self.mode == 'avg':
									nb = Branch(rootNode = n, value = avg, relation = '==', std_dev = std_dev)
									n.branches.append(nb)
								elif self.mode == 'between':
									res.sort()
									nb1 = Branch(rootNode = n, value = res[0], relation = '>=', std_dev = std_dev)
									n.branches.append(nb1)
									nb2 = Branch(rootNode = n, value = res[-1], relation = '<=', std_dev = std_dev)
									n.branches.append(nb2)
							else:
								#print avg, res[0]
								nb = Branch(rootNode = n, value = res[0], std_dev = std_dev)
								n.branches.append(nb)
							branch.nodes.append(n)
						#print i.label, branch.relation, branch.value

			# FIND THE TREE ROOTNODE
			rootnode = nodes[0]
			rootSDR = 0 # Standard Deviation Reduction: the largest the better

			# Global DATASET ATTRIBUTES
			resGlobal = []
			resGlobal = dml.list_get_column(self.datamatrix, self.target_index)
			resGlobalcopy = []
			resGlobalcopy.extend(resGlobal)
			nGlobal = 1 #  Count Elements.
			avgGlobal = 1 # Average (Avg) is the value in the leaf nodes(branch value).
			std_devGlobal = 1 # Standard Deviation (S) is for tree building (branching)
			if not list_isnumeric(resGlobalcopy):
				resGlobalcopy = dml.vector_get_distinct(resGlobalcopy)
				for index in range(len(resGlobalcopy)):
					resGlobalcopy[index] = index+1
			else:
				for index in range(len(resGlobalcopy)):
					resGlobalcopy[index] = Decimal(resGlobalcopy[index])
			#print resGlobalcopy
			nGlobal = len(resGlobalcopy)
			avgGlobal = Decimal(sum(resGlobalcopy))/Decimal(nGlobal)
			aux = 0
			for s in resGlobalcopy:
				aux = aux + (s - avgGlobal)**2
			std_devGlobal = math.sqrt(aux/nGlobal)

			for i in nodes:
				# NODE Global DATASET ATTRIBUTES
				node_std_reduction = 0.0 # Standard Deviation
				resGlobal = []
				for branch in i.branches:
					branchMatrix = branch.get_models()
					resGlobal = resGlobal + dml.list_get_column_distinct(branchMatrix, self.target_index)
				node_resGlobalcopy = []
				node_resGlobalcopy.extend(resGlobal)
				node_nGlobal = 1 #  Count Elements.
				node_avgGlobal = 1 # Average (Avg) is the value in the leaf nodes(branch value).
				node_std_devGlobal = 1 # Standard Deviation (S) is for tree building (branching)
				if not list_isnumeric(node_resGlobalcopy):
					for index in range(len(node_resGlobalcopy)):
						node_resGlobalcopy[index] = index+1
				else:
					for index in range(len(node_resGlobalcopy)):
						node_resGlobalcopy[index] = Decimal(node_resGlobalcopy[index])
				node_nGlobal = len(node_resGlobalcopy)
				node_avgGlobal = Decimal(sum(node_resGlobalcopy))/Decimal(node_nGlobal)
				aux = 0
				for s in node_resGlobalcopy:
					aux = aux + (s - node_avgGlobal)**2
				node_std_devGlobal = math.sqrt(aux/node_nGlobal)
				# 
				node_std_devs = 0 # Standard Deviation
				for branch in i.branches:
					branchMatrix = branch.get_models()
					resLocal = dml.list_get_column_distinct(branchMatrix, self.target_index)
					# MEASURE STD_DEV HERE!!!!!!!!
					resLocalcopy = []
					resLocalcopy.extend(resLocal)
					nLocal = 1 #  Count Elements.
					avgLocal = 1 # Average (Avg) is the value in the leaf nodes(branch value).
					std_devLocal = 1 # Standard Deviation (S) is for tree building (branching)
					cvLocal = [] # Coefficient of Deviation (CV) is used to decide when to stop branching. We can use Count (n) as well.
					if not list_isnumeric(resLocalcopy):
						for index in range(len(resLocalcopy)):
							resLocalcopy[index] = index+1
						nLocal = len(resLocalcopy)
						if nLocal < 1:
							break
						for j in range(len(resLocalcopy)):
							resLocalcopy[j] = Decimal(resLocalcopy[j])
						avgLocal = Decimal(sum(resLocalcopy))/Decimal(nLocal)
						aux = 0
						for s in resLocalcopy:
							aux = aux + (s - avgLocal)**2
						std_devLocal = math.sqrt(aux/nLocal)
						node_std_devs = node_std_devs + (nLocal/node_nGlobal)*std_devLocal
					else:
						nLocal = len(resLocalcopy)
						if nLocal < 1:
							break
						for j in range(len(resLocalcopy)):
							resLocalcopy[j] = Decimal(resLocalcopy[j])
						avgLocal = Decimal(sum(resLocalcopy))
						avgLocal = avgLocal/Decimal(nLocal)
						aux = 0
						for s in resLocalcopy:
							aux = aux + (s - avgLocal)**2
						std_devLocal = math.sqrt(aux/nLocal)
						node_std_devs = node_std_devs + (nLocal/node_nGlobal)*std_devLocal
					node_std_reduction = node_std_reduction +  std_devGlobal - node_std_devs
				if node_std_reduction > rootSDR:
					rootnode = i
					rootSDR = node_std_reduction # Standard Deviation Reduction: the largest the better

			# ROOTNODE FOUND
			self.root = rootnode
			"""
			# BRANCH IT
			for branch in self.root.branches:
				#print self.root.label, branch.value
				#print '|-|-|',branch.value
				#print 'RES:',branch.get_models()
				#print "--------------"
				branchMatrix = branch.get_models()
				res = dml.list_get_column_distinct(branchMatrix, self.target_index)
				# MEASURE STD_DEV HERE!!!!!!!!
				rescopy = []
				rescopy.extend(res)
				n = 1 #  Count Elements.
				avg = 1 # Average (Avg) is the value in the leaf nodes(branch value).
				std_dev = 1 # Standard Deviation (S) is for tree building (branching)
				cv = 0 # Coefficient of Deviation (CV) is used to decide when to stop branching. We can use Count (n) as well.
				if not list_isnumeric(rescopy):
					for index in range(len(rescopy)):
						rescopy[index] = index+1
					n = len(rescopy)
					avg = Decimal(sum(rescopy))/Decimal(n)
					aux = 0
					for s in rescopy:
						aux = aux + (s - avg)**2
					std_dev = math.sqrt(aux/n)
					cv = std_dev/avg*100
				else:
					n = len(rescopy)
					avg = Decimal(sum(rescopy))/Decimal(n)
					aux = 0
					for s in rescopy:
						aux = aux + (s - avg)**2
					std_dev = math.sqrt(aux/n)
					cv = std_dev/avg*100
					pass
				#print self.root.label, branch.value
				if cv > self.std_cv:
					th = []
					th.extend(tableheader)
					th.remove(self.root.label)
					branch.nodes = self.mountNodesAndBranches(th, branchMatrix, rootBranch = branch,level = level+1)
				else:
					#print self.tableheader[self.target_index],res[0]
					n = Node(tree = self, label = self.tableheader[self.target_index], index = self.target_index, rootBranch = branch,level = level+1)
					nb = Branch(rootNode = n, value = res[0])
					n.branches.append(nb)
					branch.nodes.append(n)
				"""
		return nodes
		

class Node(object):
	"""docstring for Node"""
	def __init__(self, tree = None, label = None, index = None, rootBranch = None, branches = None, level = None):
		super(Node, self).__init__()
		if tree == None:
			self.tree = None
		else:
			self.tree = tree
		if label == None:
			self.label = None
		else:
			self.label = label
		if index == None:
			self.index = None
		else:
			self.index = index
		if rootBranch == None:
			self.rootBranch = None
		else:
			self.rootBranch = rootBranch
		if branches == None:
			self.branches = []
		else:
			self.branches = branches
		if level == None:
			self.level = 0
		else:
			self.level = level


	def get_root_data(self):
		if self.rootBranch == None:
			return self.tree.datamatrix
		else:
			return self.rootBranch.get_models()

	def get_root_labels(self):
		if self.rootBranch != None:
			return self.label, self.rootBranch.get_root_labels()
		else:
			return self.label

	def predict(self, s="",vector=[], res = []):
		s = s+ '____'
		#print s + "Node: " + str(self.label)
		if len(self.branches) > 0:
			lowest_diff = Decimal('inf')
			branch = self.branches[0]
			if self.index != self.tree.target_index:
				"""
				for i in self.branches:
					d = i.belongs_to_this(vector[self.index])
					if not d:
						d = i.check_distance(vector[self.index])
						if d < lowest_diff:
							lowest_diff = d
							branch = i
					else:
						lowest_diff = 0
						branch = i
						break
				branch.predict(s,vector)
				else:
					"""
				for i in self.branches:
					if i. belongs_to_this(vector[self.index]):
						res.append(i.predict(s,vector))
			else:
				for i in self.branches:
					res.append(i.predict(s,vector))
		return res


	def showTree(self, s=""):
		s = s+ '____'
		#print s + "Node: " + str(self.label)
		if len(self.branches) > 0:
			for i in self.branches:
				i.showTree(s)

	def countMinLevel(self, depth = 0):
		n = None
		b = None
		if len(self.branches) > 0:
			for i in self.branches:
				l = i.countMinLevel(depth+1)
				if n == None:
					n = l
					b = i
				elif n > l:
					n = l
					b = i
			depth = n
		return depth, b
		

class Branch(object):
	"""docstring for Branch"""
	def __init__(self, rootNode = None, value = None, relation = None, nodes = None, std_dev = None):
		super(Branch, self).__init__()
		if rootNode == None:
			self.rootNode = None
		else:
			self.rootNode = rootNode
		if value == None:
			self.value = None
		else:
			self.value = value
		if relation == None:
			self.relation = '=='
		else:
			self.relation = relation
		if nodes == None:
			self.nodes = []
		else:
			self.nodes = nodes
		if std_dev == None:
			self.std_dev = []
		else:
			self.std_dev = std_dev
	
	def get_models(self):
		return dml.list_get_where(self.rootNode.get_root_data(), self.rootNode.index, self.value, relation = self.relation)

	def get_root_labels(self):
		if self.rootNode != None:
			return self.rootNode.get_root_labels()

	def belongs_to_this(self, value):
		s = 'self.value '
		if self.relation != '==' and isnumeric(value):
			s = 'not ' + s + self.relation +' Decimal(value)'
		else:
			s = s + self.relation + ' value'
		if eval(s):
			return True
		else:
			return False

	def check_distance(self, value):
		if isnumeric(value) and isnumeric(self.value):
			return abs(Decimal(value)-Decimal(self.value))
		else:
			return Decimal('inf')

	def predict(self, s="",vector=[]):
		s = s+ '____|'
		print s +str(self.rootNode.level)+" - "+ str(self.rootNode.label)+": " + self.relation + ' ' + str(self.value) #+ '; std_dev(' + str(self.std_dev) + ')'
		#print s, self.get_models()
		#if self.rootNode.index < len (vector) and self.belongs_to_this(vector[self.rootNode.index]) or self.rootNode.index == self.rootNode.tree.target_index:
		if len(self.nodes) > 0:
			for i in self.nodes:
				i.predict(s,vector)
		else:
			return self.rootNode

	def showTree(self, s=""):
		s = s+ '____|'
		print s +str(self.rootNode.level)+" - "+ str(self.rootNode.label)+": " + self.relation + ' ' + str(self.value) #+ '; std_dev(' + str(self.std_dev) + ')'
		if len(self.nodes) > 0:
			for i in self.nodes:
				i.showTree(s)

	def countMinLevel(self, depth = 0):
		n = None
		if len(self.nodes) > 0:
			for i in self.nodes:
				l = i.countMinLevel(depth)
				if n == None:
					n = l
				elif n > l:
					n = l
			depth = n
		return depth