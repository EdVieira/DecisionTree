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
	# It checks if the element v is a numeric data
	try:
		t = Decimal(v)
		return True
	except Exception as e:
		return False

def list_isnumeric(l):
	# It checks if the list l elements are numeric data
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

	def mountNodesAndBranches(self, tableheader, datamatrix, rootBranch = None, level = 0):
		datamatrix.sort()

		if rootBranch == None:
			# If there is no Root Node
			nodes = []
			# Create Nodes for each column related to tableheader that's not the target column
			for i in range(len(tableheader)):
				# get the column index from tableheader
				tindex = self.tableheader.index(tableheader[i])
				# If the present column is not the target column, then make it a Node
				if tindex != self.target_index:
					n = Node(tree = self, label = tableheader[i], index = tindex, rootBranch = rootBranch,level = level)
					nodes.append(n)
			# Create each node branches
			for i in range(len(nodes)):
				# Create node branches
				nodes[i] = self.create_node_branches(nodes[i], datamatrix)
			# Chose root Node
			self.choose_rootNode(nodes)
			# Check branching possibility for each Branch added to this node
			self.branching_possibility(self.root, level, tableheader)


		if rootBranch != None:
			# If there is Root Node
			nodes = []
			# ADD remaining nodes (related to the column label)
			for i in range(len(tableheader)):
				# get the column index from tableheader
				tindex = self.tableheader.index(tableheader[i])
				# if it's not the target index and if it wasn't mentioned by its parents
				if tindex != self.target_index and tableheader[i] not in rootBranch.get_root_labels():
					# create node
					n = Node(tree = self, label = tableheader[i], index = tindex, rootBranch = rootBranch,level = level)
					nodes.append(n)

			# Check branch possibility for each node
			for i in range(len(nodes)):
				# Create node branches
				nodes[i] = self.create_node_branches(nodes[i], datamatrix)
				# Check branching possibility for each Branch added to this node
				self.branching_possibility(nodes[i], level, tableheader)
			self.nodes = nodes
		return nodes
		
	def branching_possibility(self, node, level, tableheader):
		i = node
		# Check branching possibility for each Branch added to this node
		for branch in i.branches:
			# Get its filtered matrix
			branchMatrix = branch.get_models()
			# Get the distinct values from target column
			res = dml.list_get_column(branchMatrix, self.target_index)
			rescopy = []
			rescopy.extend(res)

			# Prepare the data
			# Check if target index is not numeric
			isn, rescopy = self.prepare_data(rescopy)

			# MEASURE TARGET COLUMN STANDARD DEVIATION and its coefficient
			# Measure statistics
			n, avg, std_dev, cv = self.statistics(rescopy)
			# check standard cv trigger to stop or keep branching
			if cv > self.std_cv and len(tableheader)>2:
				# keep recursive branching
				self.keep_branching(i, branch, level, tableheader, branchMatrix)
			else:
				# stop recursive branching and add leaf node to last branch
				self.stop_branching_add_leaf(branch, level, res, isn, avg, std_dev)

	def prepare_data(self, res):
		isnumdata = False
		if not list_isnumeric(res):
			res = dml.vector_get_distinct(res)
			for index in range(len(res)):
				res[index] = index+1
		else:
			for index in range(len(res)):
				res[index] = Decimal(res[index])
			isnumdata = True
		return isnumdata, res

	def statistics(self, res):
		n = len(res) #  Count Elements.
		avg = Decimal(sum(res))/Decimal(n) # Average (Avg) is the value in the leaf nodes(branch value).
		aux = Decimal(0.0)
		for s in res:
			aux = aux + (s - avg)**2
		std_dev = Decimal(math.sqrt(aux/n)) # Standard Deviation (S) is for tree building (branching)
		if std_dev != avg:
			cv = std_dev/avg*100 # Coefficient of Deviation (CV) is used to decide when to stop branching. We can use Count (n) as well.
		else:
			cv = 0
		return n, avg, std_dev, cv

	def create_node_branches(self, node, datamatrix):
		# Get distinct values from this node corresponding column
		column_values = dml.list_get_column(datamatrix, node.index)
		# Check if the values from the column of this node are numeric
		if not list_isnumeric(column_values):
			# If it is NOT numeric
			distincts = dml.vector_get_distinct(column_values)
			# Add a branch for each distinct value
			for j in range(len(distincts)):
				if distincts[j] not in node.get_root_labels():
					t = Branch(rootNode = node, value = distincts[j])
					node.branches.append(t)
		else:
			# If it IS numeric
			# Get from node all of the column values
			column_values = dml.list_get_column(node.get_root_data(), node.index)
			# Prepare data
			isn, column_values = self.prepare_data(column_values)
			# Measure statistics
			n, avg, std_dev, cv = self.statistics(column_values)
			distincts = dml.vector_get_distinct(column_values)
			if len(distincts) > 1:
				distincts = ['<=','>']
			else:
				# verify if its above or under the global average
				global_column_values = dml.list_get_column(self.datamatrix, node.index)
				# Prepare data
				isn, global_column_values = self.prepare_data(global_column_values)
				# Get average
				global_column_values_avg = sum(global_column_values)/len(global_column_values)
				if avg > global_column_values_avg:
					distincts = ['>']
					avg = avg - Decimal(0.0001)
				else:
					avg = avg + Decimal(0.0001)
					distincts = ['<']
			# Add a branch for each distinct value
			for j in range(len(distincts)):
				t = Branch(rootNode = node, value = avg, relation = distincts[j])
				node.branches.append(t)
		return node

	def choose_rootNode(self, nodes):
		# SUPOSE A ROOTNODE
		rootnode = nodes[0]
		rootSDR = 0 # Standard Deviation Reduction: the largest the better

		# Global DATASET ATTRIBUTES
		resGlobal = []
		# Get the node data
		resGlobal = dml.list_get_column(self.datamatrix, self.target_index)
		# Duplicate it
		resGlobalcopy = []
		resGlobalcopy.extend(resGlobal)
		# Prepare the data
		isn, resGlobalcopy = self.prepare_data(resGlobalcopy)
		# Measure statistics
		nGlobal, avgGlobal,std_devGlobal, cv = self.statistics(resGlobalcopy)

		for i in nodes:
			# NODE Global DATASET ATTRIBUTES
			node_std_reduction = Decimal(0) # Standard Deviation
			resGlobal = []
			for branch in i.branches:
				branchMatrix = branch.get_models()
				resGlobal = resGlobal + dml.list_get_column_distinct(branchMatrix, self.target_index)
			node_resGlobalcopy = []
			node_resGlobalcopy.extend(resGlobal)
			#Prepare the data
			isn, node_resGlobalcopy = self.prepare_data(node_resGlobalcopy)
			# Measure statistics
			node_nGlobal, node_avgGlobal, node_std_devGlobal, cv = self.statistics(node_resGlobalcopy)
			node_std_devs = Decimal(0) # Standard Deviation
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
				#Prepare the data
				isn, resLocal = self.prepare_data(resLocal)
				# Measure statistics
				nLocal, avgLocal, std_devLocal, cvLocal = self.statistics(resLocal)
				# Node Standard Deviation
				node_std_devs = node_std_devs + (nLocal/node_nGlobal)*std_devLocal 
				# Standard Deviation Reduction
				node_std_reduction = node_std_reduction +  std_devGlobal - node_std_devs
			# CHOOSE THE NODE WITH THE LARGEST STD_REDUCTION
			if node_std_reduction > rootSDR:
				rootnode = i
				rootSDR = node_std_reduction # Standard Deviation Reduction: the largest the better
		# ROOTNODE FOUND
		self.root = rootnode

	def keep_branching(self, node, branch, level, tableheader, branchMatrix):
		# keep recursive branching
		th = []
		th.extend(tableheader)
		th.remove(node.label)
		branch.nodes = self.mountNodesAndBranches(th, branchMatrix, rootBranch = branch,level = level+1)

	def stop_branching_add_leaf(self, branch, level, res, isn, avg, std_dev):
		n = Node(tree = self, label = self.tableheader[self.target_index], index = self.target_index, rootBranch = branch,level = level+1)
		nb = None
		if isn:
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
			nb = Branch(rootNode = n, value = res[0], std_dev = std_dev)
			n.branches.append(nb)
		branch.nodes.append(n)

	def showTrees(self):
		print '\nTREE_INDEX',self.root
		self.root.showTree()

	def predict(self, vector):
		return self.root.predict(vector = vector)


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
				for i in self.branches:
					if i. belongs_to_this(vector[self.index]):
						res.append(i.predict(s,vector))
			else:
				for i in self.branches:
					res.append(i.predict(s,vector))
		return res


	def showTree(self, s=""):
		s = s+ '____'
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
