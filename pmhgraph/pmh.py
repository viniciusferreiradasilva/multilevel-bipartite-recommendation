from itertools import combinations, izip, product
from random import choice, randint, sample, shuffle
import numpy as np
from igraph import Graph
import operator

class PMHGraph(Graph):

	def __init__(self, *args, **kwargs):
		super(Graph, self).__init__(*args, **kwargs)

	def projection(self, fine):
		"""
		The partitions of the reduced graph (self) is projected
		to the original/next graph (fine)
		"""

	def coarsening(self, matching):
		""" Create coarse graph """
		# Contract vertices: Referencing the original graph of the coarse graph
		uniqid = 0
		# Used to check if a vertex is already visited.
		visited = [0] * self.vcount()
		# Used to correct the types.
		types = []
		# Used to correct the weights.
		weights = []
		# Create coarsening self
		coarser = PMHGraph()
		coarser['predecessors'] = {}
		for vertex, pair in enumerate(matching):
			# Checks if the vertex is already visited.
			if visited[vertex] == 0:
				self.vs[vertex]['successor'] = uniqid
				types.append(self.vs[vertex]['type'])
				weight = self.vs[vertex]['weight']
				# If this condition is true, then a supervertex must be formed.
				if vertex != pair:
					vertex_neighbors = self['adjlist'][vertex]
					pair_neighbors = self['adjlist'][pair]
					self.vs[pair]['successor'] = uniqid
					weight += self.vs[pair]['weight']
					successors = []
					vertex_in_predecessors = vertex in self['predecessors']
					pair_in_predecessors = pair in self['predecessors']
					# Checks if the both vertices are already supervertices.
					if(vertex_in_predecessors and pair_in_predecessors):
						successors = successors + self['predecessors'][vertex] + self['predecessors'][pair]
					# Checks if the vertex is a supervertex and pair is not.
					elif(vertex_in_predecessors and not pair_in_predecessors):
						successors = successors + self['predecessors'][vertex]
						successors.append(self['predecessors'][pair])
					# Checks if the pair is a supervertex and vertex is not.
					elif(pair_in_predecessors and not vertex_in_predecessors):
						successors = successors + self['predecessors'][pair]
						successors.append(self['predecessors'][vertex])
					# If neither is a supervertex.
					else:
						successors = self['predecessors'][vertex] + self['predecessors'][pair]
					coarser['predecessors'][uniqid] = successors
				weights.append(weight)
				uniqid += 1
				visited[vertex] = 1
				visited[pair] = 1
		# Used to get the new ids after the coarsening.
		new_ids = [-1] * len(matching)
		count = 0

		for i in range(len(matching)):
			j = matching[i]
			if(i == j):
				new_ids[i] = count
				coarser['predecessors'][count] = self['predecessors'][i]
				count += 1
			elif(i != j and new_ids[j] == -1):
				new_ids[i] = count
				new_ids[j] = count
				count += 1

		coarser.add_vertices(uniqid)
		coarser.vs['type'] = types
		coarser.vs['weight'] = weights
		coarser.vs['successor'] = self.vs['successor']
		coarser['level'] = self['level'] + 1
		coarser['layers'] = self['layers']
		coarser['vertices'] = []
		for layer in xrange(self['layers']):
			coarser['vertices'].append(len(coarser.vs.select(type=layer)))

		# Contract edges
		dict_edges = dict()
		for edge in self.es():
			v_successor = self.vs[edge.tuple[0]]['successor']
			u_successor = self.vs[edge.tuple[1]]['successor']

			# Loop is not necessary
			if v_successor == u_successor: continue

			# Add edge in coarse graph
			if v_successor < u_successor:
				dict_edges[(v_successor, u_successor)] = dict_edges.get((v_successor, u_successor), 0) + edge['weight']
			else:
				dict_edges[(u_successor, v_successor)] = dict_edges.get((u_successor, v_successor), 0) + edge['weight']

		if len(dict_edges) > 0:
			edges, weights = izip(*dict_edges.items())
			coarser.add_edges(edges)
			coarser.es['weight'] = weights
			coarser['adjlist'] = map(set, coarser.get_adjlist())
		return coarser

	def greed_two_hops(self, vertices, reduction_factor, matching):
		"""
		Matches are restricted between vertices that are not adjacent
		but are only allowed to match with neighbors of its neighbors,
		i.e. two-hopes neighborhood
		"""
		merge_count = int(reduction_factor * self.vcount())
		return self.get_greed_two_hops(vertices, merge_count, matching)


	def get_greed_two_hops(self, vertices, merge_count, matching, reverse=True):
			"""
			The best match is selected for each vertex using its two-hops neighborhood
			"""
			# Search two-hopes neighborhood for each vertex in selected layer
			dict_edges = {}
			# Index that will be used to calculate the similarities.
			index = self['similarity']
			visited = [0] * self.vcount()

			numberof = 0
			for vertex in vertices:
				neighborhood = self.neighborhood(vertices=vertex, order=2)
				twohops = neighborhood[(len(self['adjlist'][vertex]) + 1):]
				for twohop in twohops:
					if visited[twohop] == 0:
						dict_edges[(vertex, twohop)] = index(vertex, twohop)
				visited[vertex] = 1

			# Select promising matches or pair of vertices
			edges = sorted(dict_edges.items(), key=operator.itemgetter(1), reverse=reverse)

			for edge, value in edges:
				if (matching[edge[0]] == edge[0]) and (matching[edge[1]] == edge[1]):
					matching[edge[0]] = edge[1]
					matching[edge[1]] = edge[0]
					merge_count -= 1
				if merge_count == 0: break


	def greed_rand_two_hops(self, vertices, reduction_factor, matching):
		"""
		TODO: description
		"""

		merge_count = int(reduction_factor * self.vcount())
		return self.get_greed_rand_two_hops(vertices, merge_count, matching)

	def get_greed_rand_two_hops(self, vertices, merge_count, matching):
		"""
		TODO: description
		"""

		visited = [0] * self.vcount()
		index = 0
		sample_vertices = sample(vertices, len(vertices))
		adjlist = map(set, self.get_adjlist())
		while merge_count > 0 and index < len(vertices):
			# Randomly select a vertex v of V
			vertex = sample_vertices[index]
			if visited[vertex] == 1:
				index += 1
				continue
			# Select the edge (v, u) of E wich maximum score
			# Tow hopes restriction: It ensures that the match only occurs between vertices of the same type
			neighborhood = self.neighborhood(vertices=vertex, order=2)
			twohops = neighborhood[(len(self['adjlist'][vertex]) + 1):]
			_max = 0.0
			neighbor = vertex
			for twohop in twohops:
				if visited[twohop] == 1: continue
				# Calling a function of a module from a string
				score = self['similarity'](vertex, twohop)
				if score > _max:
					_max = score
					neighbor = twohop
			matching[neighbor] = vertex
			matching[vertex] = neighbor
			visited[neighbor] = 1
			merge_count -= 1
			visited[vertex] = 1
			index += 1
